release: python manage.py migrate --settings=crm_project.settings_production
web: gunicorn crm_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --timeout 120 --access-logfile - --error-logfile -
worker: celery -A crm_project worker --loglevel=info
beat: celery -A crm_project beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
