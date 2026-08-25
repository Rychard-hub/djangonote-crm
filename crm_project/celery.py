"""
Celery Configuration for CRM Project
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')

app = Celery('crm_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Optional: Configure Celery to use Redis as broker
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Vilnius',
    enable_utc=True,
)

# Task routing
app.conf.task_routes = {
    'crm.tasks.*': {'queue': 'crm'},
}

# Task priorities
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1

# Error handling
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_late = True

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery connection"""
    try:
        print(f'Request: {self.request!r}')
        return 'Debug task completed successfully'
    except Exception as e:
        print(f'Debug task error: {str(e)}')
        return f'Debug task error: {str(e)}'
