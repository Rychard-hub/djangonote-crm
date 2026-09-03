from django.contrib.auth.models import User
from django.db import models

from accounts.models import Organization


class Conversation(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='conversations')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # MVP: one ongoing conversation per (organization, user) -- see
        # assistant/views.py assistant_view()'s get_or_create(). Multiple
        # named conversations per user is a natural follow-up, not MVP.
        unique_together = [('organization', 'created_by')]

    def __str__(self):
        return f'{self.created_by.username} @ {self.organization.name}'


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'Vartotojas'),
        ('assistant', 'Asistentas'),
    ]

    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:40]}'
