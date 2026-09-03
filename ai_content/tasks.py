import logging

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import ContentJob
from .services import (
    AIProviderNotConfigured,
    GenerationFailed,
    ImageProviderNotConfigured,
    generate_image_bytes,
    generate_text,
    generate_video_bytes,
)

logger = logging.getLogger(__name__)


@shared_task(name='ai_content.tasks.run_content_job')
def run_content_job(job_id):
    try:
        job = ContentJob.objects.get(pk=job_id)
    except ContentJob.DoesNotExist:
        logger.warning('run_content_job: ContentJob %s no longer exists', job_id)
        return

    job.status = 'processing'
    job.save(update_fields=['status'])

    update_fields = ['status', 'error', 'completed_at']

    try:
        if job.kind == 'image':
            file_bytes, _content_type = generate_image_bytes(job.prompt)
            job.result_file.save(f'image-{job.pk}.png', ContentFile(file_bytes), save=False)
            update_fields.append('result_file')
        elif job.kind == 'video':
            file_bytes, _content_type = generate_video_bytes(job.prompt)
            job.result_file.save(f'video-{job.pk}.mp4', ContentFile(file_bytes), save=False)
            update_fields.append('result_file')
        else:
            job.result_text = generate_text(job.kind, job.prompt)
            update_fields.append('result_text')
        job.status = 'done'
    except (AIProviderNotConfigured, ImageProviderNotConfigured, GenerationFailed) as exc:
        job.status = 'failed'
        job.error = str(exc)
    except Exception as exc:
        logger.exception('run_content_job failed for job %s', job_id)
        job.status = 'failed'
        job.error = str(exc)

    job.completed_at = timezone.now()
    job.save(update_fields=update_fields)
