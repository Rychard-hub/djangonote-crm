import logging

from celery import shared_task
from django.utils import timezone

from .models import ContentJob
from .services import AIProviderNotConfigured, generate_text

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

    try:
        job.result_text = generate_text(job.kind, job.prompt)
        job.status = 'done'
    except AIProviderNotConfigured as exc:
        job.status = 'failed'
        job.error = str(exc)
    except Exception as exc:
        logger.exception('run_content_job failed for job %s', job_id)
        job.status = 'failed'
        job.error = str(exc)

    job.completed_at = timezone.now()
    job.save(update_fields=['result_text', 'status', 'error', 'completed_at'])
