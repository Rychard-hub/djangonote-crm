from django import forms
from datetime import date, timedelta

from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from accounts.models import Organization, get_organization
from .models import Activity, Comment, Lead, Task, Profile


class EmailUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('Vartotojas su tokiu el. paštu jau užregistruotas.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


def health_check(request):
    """Public health check endpoint for Docker/reverse proxies."""
    return JsonResponse({"status": "ok", "service": "django-crm"})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'crm/login.html')


def register_view(request):
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            Organization.objects.create_for_user(user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmailUserCreationForm()

    return render(request, 'crm/register.html', {'form': form})


def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Siunčiame el. laišką (testavimui - tiesiog atspausdinam)
                reset_link = f"http://127.0.0.1:8000/reset/{uid}/{token}/"
                
                # Galima siųsti tikru el. laišką jeigu nustatyta
                try:
                    send_mail(
                        'Slaptažodžio atkūrimas - Freelancer CRM',
                        f'Sveiki,\n\nNorėdami atkurti savo slaptažodį, spauskite šią nuorodą:\n{reset_link}\n\nJei jūs neprašėte slaptažodžio atkūrimo, ignoruokite šį laišką.',
                        'noreply@freelancer-crm.lt',
                        [email],
                        fail_silently=True,
                    )
                except:
                    # Testavimui - tiesiog rodome nuorodą
                    pass
                
                return render(request, 'crm/password_reset_done.html', {'email': email})
            except User.DoesNotExist:
                form.add_error('email', 'Vartotojas su tokiu el. paštu nerastas')
    else:
        form = PasswordResetForm()
    
    return render(request, 'crm/password_reset.html', {'form': form})


@login_required(login_url='login')
def dashboard_view(request):
    organization = get_organization(request.user)
    user_leads = Lead.objects.filter(organization=organization)
    today = date.today()
    
    # Realūs duomenys metrikoms
    context = {
        'today_followups': user_leads.filter(next_follow_up=today).count(),
        'new_leads': user_leads.filter(status='new').count(),
        'waiting_leads': user_leads.filter(status='contacted').count(),
        'won_projects': user_leads.filter(status='won').count(),
        'lost_projects': user_leads.filter(status='lost').count(),
        # Artimiausi follow-up'ai (realūs duomenys)
        'upcoming_followups': user_leads.filter(
            next_follow_up__gte=today
        ).order_by('next_follow_up')[:5],
        # Vėluojantys kontaktai (realūs duomenys)
        'overdue_contacts': user_leads.filter(
            next_follow_up__lt=today
        ).order_by('next_follow_up')[:5],
        # Paskutiniai atnaujinti lead'ai
        'recent_leads': user_leads.order_by('-updated_at')[:5],
        # Šiandienos užduotys
        'today_tasks': Task.objects.filter(
            lead__organization=organization,
            completed=False
        ).order_by('created_at')[:5],
        'today': today,
    }
    return render(request, 'crm/dashboard.html', context)


@login_required(login_url='login')
def followup_list_view(request):
    today = date.today()
    filter_type = request.GET.get('filter', 'today')
    queryset = Lead.objects.filter(organization=get_organization(request.user), next_follow_up__isnull=False)

    if filter_type == 'today':
        queryset = queryset.filter(next_follow_up=today)
    elif filter_type == 'overdue':
        queryset = queryset.filter(next_follow_up__lt=today)
    elif filter_type == 'week':
        queryset = queryset.filter(next_follow_up__range=[today, today + timedelta(days=7)])

    queryset = queryset.order_by('next_follow_up', 'name')

    context = {
        'followups': queryset,
        'filter_type': filter_type,
        'today': today,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_followup_content.html', context)
    return render(request, 'crm/followup_list.html', context)


PIPELINE_STAGES = Lead.STATUS_CHOICES


def _pipeline_columns(organization):
    codes = [code for code, _ in PIPELINE_STAGES]
    columns = []
    for i, (code, label) in enumerate(PIPELINE_STAGES):
        leads = Lead.objects.filter(organization=organization, status=code).order_by('next_follow_up', 'name')
        columns.append({
            'code': code,
            'label': label,
            'leads': leads,
            'prev_code': codes[i - 1] if i > 0 else None,
            'next_code': codes[i + 1] if i < len(codes) - 1 else None,
        })
    return columns


@login_required(login_url='login')
def pipeline_view(request):
    return render(request, 'crm/pipeline.html', {'columns': _pipeline_columns(get_organization(request.user))})


@login_required(login_url='login')
def lead_pipeline_move_view(request, pk, status):
    organization = get_organization(request.user)
    lead = get_object_or_404(Lead, pk=pk, organization=organization)
    if request.method == 'POST':
        lead.status = status
        lead.save()
        Activity.objects.create(lead=lead, action='status_change', details=f'Statusas pakeistas į {lead.get_status_display()}', created_by=request.user)

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_kanban_board.html', {'columns': _pipeline_columns(organization)})
    return redirect('pipeline')


@login_required(login_url='login')
def settings_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        reminder_days = request.POST.get('reminder_days', '1').strip()
        timezone = request.POST.get('timezone', 'Europe/Vilnius').strip()
        organization = request.POST.get('organization', '').strip()

        if full_name:
            user.first_name = full_name
            user.last_name = ''
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        
        profile.reminder_days = int(reminder_days) if reminder_days.isdigit() else 1
        profile.timezone = timezone
        profile.organization = organization
        profile.save()

    context = {
        'full_name': request.user.first_name or '',
        'email': request.user.email or '',
        'reminder_days': profile.reminder_days,
        'timezone': profile.timezone,
        'organization': profile.organization,
    }
    return render(request, 'crm/settings.html', context)


@login_required(login_url='login')
def lead_list_view(request):
    leads = Lead.objects.filter(organization=get_organization(request.user))
    today = date.today()
    
    # Filtrai
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    followup_filter = request.GET.get('followup', '')
    
    # Paieška
    if query:
        leads = leads.filter(
            name__icontains=query
        ) | leads.filter(
            company__icontains=query
        ) | leads.filter(
            email__icontains=query
        )
    
    # Statuso filtras
    if status:
        leads = leads.filter(status=status)
    
    # Follow-up filtras
    if followup_filter == 'today':
        leads = leads.filter(next_follow_up=today)
    elif followup_filter == 'overdue':
        leads = leads.filter(next_follow_up__lt=today)
    elif followup_filter == 'upcoming':
        leads = leads.filter(next_follow_up__gt=today)
    
    # Rūšiavimas
    sort_by = request.GET.get('sort', '-updated_at')
    leads = leads.order_by(sort_by)

    # Statistika
    context = {
        'leads': leads,
        'query': query,
        'status': status,
        'followup_filter': followup_filter,
        'sort_by': sort_by,
        'total_leads': leads.count(),
        'today': today,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_lead_list_response.html', context)
    return render(request, 'crm/lead_list.html', context)


@login_required(login_url='login')
def lead_create_view(request):
    if request.method == 'POST':
        Lead.objects.create(
            name=request.POST.get('name', '').strip(),
            company=request.POST.get('company', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            source=request.POST.get('source', '').strip(),
            status=request.POST.get('status', 'new'),
            last_contacted=request.POST.get('last_contacted') or None,
            next_follow_up=request.POST.get('next_follow_up') or None,
            budget=request.POST.get('budget', '0') or '0',
            notes=request.POST.get('notes', '').strip(),
            owner=request.user,
            organization=get_organization(request.user),
        )
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('lead-list')
            return response
        return redirect('lead-list')

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_lead_form_modal.html', {'mode': 'create'})
    return render(request, 'crm/lead_form.html', {'mode': 'create'})


@login_required(login_url='login')
def lead_detail_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    today = date.today()
    
    # Papildomi duomenys
    comments = lead.comments.all()
    tasks = lead.tasks.all()
    activities = lead.activities.all()
    
    # Skaičiuojame statistiką
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    # Follow-up statusas
    days_until_followup = None
    if lead.next_follow_up:
        if lead.next_follow_up < today:
            days_until_followup = (today - lead.next_follow_up).days  # Teigiamas skaičius = kiek dienų vėluoja
        else:
            days_until_followup = (lead.next_follow_up - today).days  # Teigiamas skaičius = dienos iki
    
    context = {
        'lead': lead,
        'comments': comments,
        'tasks': tasks,
        'activities': activities,
        'today': today,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'days_until_followup': days_until_followup,
        'is_overdue': lead.next_follow_up and lead.next_follow_up < today,
        'is_today': lead.next_follow_up == today,
        'status_choices': Lead.STATUS_CHOICES,
    }
    return render(request, 'crm/lead_detail.html', context)


@login_required(login_url='login')
def lead_edit_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))

    if request.method == 'POST':
        lead.name = request.POST.get('name', '').strip()
        lead.company = request.POST.get('company', '').strip()
        lead.email = request.POST.get('email', '').strip()
        lead.phone = request.POST.get('phone', '').strip()
        lead.source = request.POST.get('source', '').strip()
        lead.status = request.POST.get('status', 'new')
        lead.last_contacted = request.POST.get('last_contacted') or None
        lead.next_follow_up = request.POST.get('next_follow_up') or None
        lead.budget = request.POST.get('budget', '0') or '0'
        lead.notes = request.POST.get('notes', '').strip()
        lead.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('lead-detail', kwargs={'pk': lead.pk})
            return response
        return redirect('lead-detail', pk=lead.pk)

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_lead_form_modal.html', {'mode': 'edit', 'lead': lead})
    return render(request, 'crm/lead_form.html', {'mode': 'edit', 'lead': lead})


@login_required(login_url='login')
def lead_delete_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    if request.method == 'POST':
        lead.delete()
        return redirect('lead-list')
    return render(request, 'crm/lead_confirm_delete.html', {'lead': lead})


@login_required(login_url='login')
def lead_status_update_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    if request.method == 'POST':
        lead.status = request.POST.get('status', lead.status)
        lead.save()
    return redirect('lead-list')


@login_required(login_url='login')
def lead_comment_add_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    comment = None
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        kind = request.POST.get('kind', 'note')
        author = request.POST.get('author', 'Sistema').strip() or 'Sistema'
        if body:
            comment = Comment.objects.create(lead=lead, body=body, kind=kind, author=author, created_by=request.user)

    if request.headers.get('HX-Request'):
        if comment is None:
            return HttpResponse('')
        return render(request, 'crm/partials/_comment_add_response.html', {'comment': comment})
    return redirect('lead-detail', pk=lead.pk)


@login_required(login_url='login')
def lead_reminder_send_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    sent = False
    if request.method == 'POST' and lead.email:
        send_mail(
            subject=f'Priminimas apie leadą {lead.name}',
            message=f'Sveiki, tai priminimas apie leadą {lead.name} ({lead.company}).\nKitas follow-up: {lead.next_follow_up or "nenurodyta"}.',
            from_email='noreply@example.com',
            recipient_list=[lead.email],
            fail_silently=True,
        )
        sent = True

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_reminder_status.html', {'sent': sent})
    return redirect('lead-detail', pk=lead.pk)


@login_required(login_url='login')
def lead_task_add_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    task = None
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            task = Task.objects.create(lead=lead, title=title, created_by=request.user)
            Activity.objects.create(lead=lead, action='task_added', details=title, created_by=request.user)

    if request.headers.get('HX-Request'):
        if task is None:
            return HttpResponse('')
        return render(request, 'crm/partials/_task_add_response.html', {'task': task})
    return redirect('lead-detail', pk=lead.pk)


@login_required(login_url='login')
def task_toggle_view(request, pk):
    task = get_object_or_404(Task, pk=pk, lead__organization=get_organization(request.user))
    task.completed = not task.completed
    task.save()
    Activity.objects.create(lead=task.lead, action='task_toggled', details=task.title, created_by=request.user)

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_task_item.html', {'task': task})
    return redirect('lead-detail', pk=task.lead.pk)


@login_required(login_url='login')
def lead_quick_action_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'reminder':
            Activity.objects.create(lead=lead, action='reminder_sent', details='Priminimas išsiųstas', created_by=request.user)
        elif action == 'note':
            Activity.objects.create(lead=lead, action='note_added', details='Pastaba pridėta', created_by=request.user)
    return redirect('lead-list')


@login_required(login_url='login')
def lead_status_mark_view(request, pk, status):
    lead = get_object_or_404(Lead, pk=pk, organization=get_organization(request.user))
    if request.method == 'POST':
        lead.status = status
        lead.save()
        Activity.objects.create(lead=lead, action='status_change', details=f'Statusas pakeistas į {lead.get_status_display()}', created_by=request.user)

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_status_badge.html', {'lead': lead})
    return redirect('lead-detail', pk=lead.pk)
