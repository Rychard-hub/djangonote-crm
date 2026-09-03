from django.contrib.auth.models import User
from django.db import models

from accounts.models import Organization


class ContentJob(models.Model):
    # script/headline generate text via services.generate_text(); image/video
    # generate a file via services.generate_image_bytes()/generate_video_bytes()
    # (Stability AI). All four now have working handlers in ai_content/tasks.py
    # -- see the PIPELINE_STAGES fix in crm for what happens when a choice
    # ships ahead of the code that handles it.
    KIND_CHOICES = [
        ('script', 'Scenarijus'),
        ('headline', 'Antraštė'),
        ('image', 'Vaizdas'),
        ('video', 'Video'),
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
    result_file = models.FileField(upload_to='ai_content/', null=True, blank=True)
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

    @property
    def is_media(self):
        return self.kind in ('image', 'video')
