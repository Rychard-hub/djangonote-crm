from django.contrib.auth.models import User
from django.db import models

from accounts.models import Organization


class ContentJob(models.Model):
    # Only kinds services.generate_text() actually implements. Image/video
    # are the intended follow-up (docs/bussynote-mvp-architecture.md
    # section 6) but adding those choices before the generation logic
    # exists would put an unreachable option in front of users -- see the
    # PIPELINE_STAGES fix in crm for the same mistake made once already.
    KIND_CHOICES = [
        ('script', 'Scenarijus'),
        ('headline', 'Antraštė'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Laukia'),
        ('processing', 'Vykdoma'),
        ('done', 'Atlikta'),
        ('failed', 'Klaida'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='content_jobs')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_jobs')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    prompt = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_text = models.TextField(blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_kind_display()}: {self.prompt[:40]}'

    @property
    def in_progress(self):
        return self.status in ('pending', 'processing')
