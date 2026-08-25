from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class EmailVerification(models.Model):
    """El. pašto patvirtinimo token'ų modelis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Verification for {self.user.email} - {self.token}"
    
    def is_expired(self):
        """Tikrina ar token'as nebegaliojęs (24 valandos)"""
        return (timezone.now() - self.created_at).total_seconds() > 86400


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100, blank=True, help_text="Organization or company name")
    timezone = models.CharField(max_length=50, default='Europe/Vilnius')
    reminder_days = models.PositiveIntegerField(default=1)
    email_verified = models.BooleanField(default=False, help_text="Ar el. paštas patvirtintas")
    
    def __str__(self):
        return f"{self.user.username} - {self.organization or 'Personal'}"


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Naujas'),
        ('contacted', 'Susisiekta'),
        ('proposal', 'Pasiūlymas'),
        ('won', 'Laimėtas'),
        ('lost', 'Prarastas'),
    ]

    name = models.CharField(max_length=100)
    company = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    source = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    last_contacted = models.DateField(blank=True, null=True)
    next_follow_up = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.company or 'Lead'


class Comment(models.Model):
    TYPE_CHOICES = [
        ('note', 'Pastaba'),
        ('call', 'Skambutis'),
        ('email', 'El. laiškas'),
        ('message', 'Žinutė'),
    ]

    lead = models.ForeignKey(Lead, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    author = models.CharField(max_length=100, default='Sistema')
    kind = models.CharField(max_length=20, choices=TYPE_CHOICES, default='note')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.lead.name}: {self.body[:30]}'


class Task(models.Model):
    lead = models.ForeignKey(Lead, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['completed', 'created_at']

    def __str__(self):
        return self.title


class Activity(models.Model):
    lead = models.ForeignKey(Lead, related_name='activities', on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.lead:
            return f'{self.lead.name}: {self.action}'
        return f'{self.action}: {self.details[:30]}'
