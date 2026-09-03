# Railway deploy image. One image, three process types (web/worker/beat) --
# each Railway service points at this same Dockerfile and overrides the
# start command (see Procfile / RAILWAY.md) rather than each getting its
# own image. Postgres, Redis, and file storage (Cloudflare R2) are all
# external managed services -- nothing is baked into this image.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=crm_project.settings_production

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_production.txt /app/
RUN pip install --no-cache-dir -r requirements_production.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media

# Static assets don't depend on runtime secrets (DB, API keys), so this is
# safe to run at build time -- it just needs the settings module to import.
RUN python manage.py collectstatic --noinput --settings=crm_project.settings_production

EXPOSE 8000

# Shell form (not exec-array form) so $PORT/$WEB_CONCURRENCY actually expand.
# Railway injects $PORT at runtime; the web service uses this CMD as-is,
# worker/beat services override it with a Custom Start Command instead.
CMD gunicorn crm_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
