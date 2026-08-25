from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.db.models import Count, Q, Sum
from datetime import date, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

from django.contrib.auth.models import User
from .models import Lead, Comment, Task, Activity, Profile, EmailVerification
from .serializers import (
    LeadSerializer, LeadDetailSerializer, LeadCreateSerializer, LeadStatusUpdateSerializer,
    CommentSerializer, CommentCreateSerializer,
    TaskSerializer, TaskCreateSerializer,
    ActivitySerializer,
    ProfileSerializer
)


class LeadViewSet(viewsets.ModelViewSet):
    """
    Lead'ų ViewSet su CRUD operacijomis ir papildomais veiksmais
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source']
    search_fields = ['name', 'company', 'email', 'notes']
    ordering_fields = ['name', 'created_at', 'updated_at', 'next_follow_up', 'budget']
    ordering = ['-updated_at']

    def get_queryset(self):
        return Lead.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LeadCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return LeadDetailSerializer
        return LeadSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Gauti dashboard statistiką"""
        user_leads = Lead.objects.filter(owner=request.user)
        today = date.today()
        
        stats = {
            'total_leads': user_leads.count(),
            'new_leads': user_leads.filter(status='new').count(),
            'contacted_leads': user_leads.filter(status='contacted').count(),
            'proposal_leads': user_leads.filter(status='proposal').count(),
            'won_leads': user_leads.filter(status='won').count(),
            'lost_leads': user_leads.filter(status='lost').count(),
            'today_followups': user_leads.filter(next_follow_up=today).count(),
            'overdue_followups': user_leads.filter(next_follow_up__lt=today).count(),
            'total_budget': user_leads.aggregate(total=models.Sum('budget'))['total'] or 0,
            'won_budget': user_leads.filter(status='won').aggregate(total=models.Sum('budget'))['total'] or 0,
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def upcoming_followups(self, request):
        """Gauti artėjančius follow-up'us"""
        days = int(request.query_params.get('days', 7))
        today = date.today()
        end_date = today + timedelta(days=days)
        
        leads = self.get_queryset().filter(
            next_follow_up__gte=today,
            next_follow_up__lte=end_date
        ).order_by('next_follow_up')
        
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue_followups(self, request):
        """Gauti vėluojančius follow-up'us"""
        today = date.today()
        leads = self.get_queryset().filter(
            next_follow_up__lt=today
        ).order_by('next_follow_up')
        
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Atnaujinti lead'o statusą"""
        lead = self.get_object()
        serializer = LeadStatusUpdateSerializer(lead, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            # Sukuriam activity įrašą
            Activity.objects.create(
                lead=lead,
                action='status_change',
                details=f'Statusas pakeistas į {lead.get_status_display()}',
                created_by=request.user
            )
            return Response(LeadSerializer(lead).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Pridėti komentarą prie lead'o"""
        lead = self.get_object()
        serializer = CommentCreateSerializer(
            data=request.data, 
            context={'lead_id': lead.id, 'request': request}
        )
        
        if serializer.is_valid():
            comment = serializer.save()
            # Sukuriam activity įrašą
            Activity.objects.create(
                lead=lead,
                action='comment_added',
                details=f'Komentaras pridėtas: {comment.body[:50]}...',
                created_by=request.user
            )
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Pridėti užduotį prie lead'o"""
        lead = self.get_object()
        serializer = TaskCreateSerializer(
            data=request.data, 
            context={'lead_id': lead.id, 'request': request}
        )
        
        if serializer.is_valid():
            task = serializer.save()
            # Sukuriam activity įrašą
            Activity.objects.create(
                lead=lead,
                action='task_added',
                details=f'Užduotis pridėta: {task.title}',
                created_by=request.user
            )
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Gauti lead'o veiksmų istoriją"""
        lead = self.get_object()
        activities = lead.activities.all().order_by('-created_at')
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Komentarų ViewSet
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['kind', 'lead']
    ordering = ['-created_at']

    def get_queryset(self):
        return Comment.objects.filter(lead__owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        # Patikriname ar vartotojas turi teisę šiam lead'ui
        lead_id = serializer.validated_data['lead'].id
        if not Lead.objects.filter(id=lead_id, owner=self.request.user).exists():
            raise permissions.PermissionDenied("Neturite teisės šiam lead'ui")
        
        serializer.save(created_by=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Užduočių ViewSet
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['completed', 'lead']
    ordering = ['completed', '-created_at']

    def get_queryset(self):
        return Task.objects.filter(lead__owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        # Patikriname ar vartotojas turi teisę šiam lead'ui
        lead_id = serializer.validated_data['lead'].id
        if not Lead.objects.filter(id=lead_id, owner=self.request.user).exists():
            raise permissions.PermissionDenied("Neturite teisės šiam lead'ui")
        
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def toggle_complete(self, request, pk=None):
        """Perjungti užduoties būseną"""
        task = self.get_object()
        task.completed = not task.completed
        task.save()
        
        # Sukuriam activity įrašą
        Activity.objects.create(
            lead=task.lead,
            action='task_toggled',
            details=f'Užduotis "{task.title}" {"atlikta" if task.completed else "neatlikta"}',
            created_by=request.user
        )
        
        return Response(TaskSerializer(task).data)


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Veiksmų istorijos ViewSet (tik skaitymui)
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivitySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'lead']
    ordering = ['-created_at']

    def get_queryset(self):
        return Activity.objects.filter(lead__owner=self.request.user)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Vartotojo profilio ViewSet
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    @action(detail=False, methods=['post'])
    def send_invitation(self, request):
        """
        Siunčia el. laišką su nuoroda į naujos paskyros kūrimo formą
        """
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'El. pašto adresas būtinas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Generuojame specialų token'ą
            token = default_token_generator.make_token(request.user)
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))
            
            # Sukuriame nuorodą
            invitation_link = f"{settings.FRONTEND_URL}/invite/{uid}/{token}/"
            
            # Siunčiame el. laišką
            subject = "Kvietimas prisijungti prie Freelancer CRM"
            
            context = {
                'user': request.user,
                'invitation_link': invitation_link,
                'email': email,
            }
            
            message = render_to_string('crm/email/invitation.txt', context)
            html_message = render_to_string('crm/email/invitation.html', context)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Log'iname veiksmą
            Activity.objects.create(
                action='invitation_sent',
                details=f"Pakvietimas į CRM išsiųstas į {email}",
                created_by=request.user
            )
            
            return Response({
                'success': True,
                'message': f'Kvietimas išsiųstas į {email}',
                'invitation_link': invitation_link
            })
            
        except Exception as e:
            return Response(
                {'error': f'Klaida siunčiant kvietimą: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegistrationViewSet(viewsets.ViewSet):
    """
    Registracijos ViewSet su el. pašto patvirtinimu
    """
    authentication_classes = []
    permission_classes = []
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Vartotojo registracija su el. pašto patvirtinimu
        """
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response(
                {'error': 'Visi laukai būtini'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tikriname ar vartotojas jau egzistuoja
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Vartotojas su šiuo el. paštu jau egzistuoja'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Toks vartotojo vardas jau naudojamas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Sukuriamas vartotojas (aktyvus nuo pat pradžių)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True
            )
            
            # Sukuriamas profilis
            Profile.objects.create(user=user)
            
            # Sukuriamas patvirtinimo token'as
            verification = EmailVerification.objects.create(user=user)
            
            # Siunčiamas patvirtinimo el. laiškas (jei įmanoma)
            try:
                verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification.token}"
                
                context = {
                    'user': user,
                    'verification_link': verification_link,
                }
                
                subject = "Patvirtinkite savo el. paštą - Freelancer CRM"
                message = render_to_string('crm/email/email_verification.txt', context)
                html_message = render_to_string('crm/email/email_verification.html', context)
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception:
                pass
            
            return Response({
                'success': True,
                'message': 'Registracija sėkminga! Dabar galite prisijungti.',
                'user_id': user.id
            })
            
        except Exception as e:
            return Response(
                {'error': f'Klaida registruojant: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """
        El. pašto patvirtinimas
        """
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token būtinas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Randamas patvirtinimas
            verification = EmailVerification.objects.get(token=token)
            
            # Tikriname ar token'as galioja
            if verification.is_used:
                return Response(
                    {"error": "Token'as jau panaudotas"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if verification.is_expired():
                return Response(
                    {"error": "Token'as nebegalioja"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Aktyvuojame vartotoją
            user = verification.user
            user.is_active = True
            user.save()
            
            # Pažymime el. paštą kaip patvirtintą
            profile = user.profile
            profile.email_verified = True
            profile.save()
            
            # Pažymime token'ą kaip panaudotą
            verification.is_used = True
            verification.save()
            
            # Log'iname veiksmą
            Activity.objects.create(
                action='email_verified',
                details=f"El. paštas {user.email} patvirtintas",
                created_by=user
            )
            
            return Response({
                'success': True,
                'message': 'El. paštas sėkmingai patvirtintas! Galite prisijungti.',
                'user_id': user.id
            })
            
        except EmailVerification.DoesNotExist:
            return Response(
                {"error": "Neteisingas token'as"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Klaida patvirtinant el. paštą: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
