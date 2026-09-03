from pathlib import Path
from datetime import timedelta
import os

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# BASIC
# --------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG = False

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")

# Frontend is served by same domain in production
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://yourdomain.com,http://localhost"
).split(",")

CORS_ALLOW_CREDENTIALS = True

# Django rejects unsafe (POST/PUT/...) requests whose Origin isn't listed
# here once the app sits behind a proxy like Railway's edge -- set this to
# your public URL(s), e.g. https://your-app.up.railway.app
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# --------------------------------------------------
# INSTALLED APPS
# --------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "django_extensions",
    "django_celery_beat",
    "django_celery_results",
    "storages",

    # tavo apps
    "accounts",
    "crm",
    "catalog",
    "billing",
    "ai_content",
    "assistant",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crm_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crm_project.wsgi.application"

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", "postgres://crm_user:crm_pass@db:5433/crm_db"),
        conn_max_age=600,
        # Railway's internal Postgres connection doesn't need/support SSL;
        # set to "1" if connecting over its public proxy instead.
        ssl_require=os.getenv("DATABASE_SSL_REQUIRE", "0") == "1",
    )
}

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "lt"
TIME_ZONE = "Europe/Vilnius"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC / MEDIA
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# PDF Generation Settings
PDF_ROOT = MEDIA_ROOT / "pdfs"
PDF_URL = MEDIA_URL + "pdfs/"

# Static files are baked into the container image, so WhiteNoise serves
# them straight from local disk -- no object storage needed there. Media
# (user uploads, generated PDFs/images/videos) is a different story: most
# PaaS containers (Railway included) have an ephemeral filesystem, so
# anything written to MEDIA_ROOT disappears on the next deploy/restart.
# Point AWS_STORAGE_BUCKET_NAME at an S3-compatible bucket (e.g.
# Cloudflare R2) to persist it there instead; unset, it falls back to
# local disk, same "unconfigured -> degrade" pattern used for the
# Stripe/Anthropic/Stability integrations below.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "")

if AWS_STORAGE_BUCKET_NAME:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    # e.g. https://<account_id>.r2.cloudflarestorage.com for Cloudflare R2
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "auto")
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "virtual")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = None  # R2 doesn't support per-object ACLs
    AWS_S3_FILE_OVERWRITE = False
    # Public bucket/custom domain (e.g. an r2.dev subdomain or your own
    # domain mapped to the bucket) -> plain URLs, no querystring auth.
    # Leave unset for a private bucket accessed via signed URLs instead.
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")
    AWS_QUERYSTRING_AUTH = not AWS_S3_CUSTOM_DOMAIN
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}

# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# REST FRAMEWORK
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

# --------------------------------------------------
# SIMPLE JWT
# --------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --------------------------------------------------
# CELERY / REDIS
# --------------------------------------------------
# Railway's Redis plugin injects REDIS_URL; CELERY_BROKER_URL/
# CELERY_RESULT_BACKEND only need setting explicitly if you want the
# broker and result backend to live in different places.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Vilnius"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    "send-follow-up-reminders": {
        "task": "crm.tasks.send_follow_up_reminders",
        "schedule": 60.0,  # Every minute for testing
    },
    "send-daily-reports": {
        "task": "crm.tasks.send_daily_reports",
        "schedule": 86400.0,  # Every day
    },
    "cleanup-old-activities": {
        "task": "crm.tasks.cleanup_old_activities",
        "schedule": 604800.0,  # Every week
    },
}

# --------------------------------------------------
# CACHE CONFIGURATION
# --------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# --------------------------------------------------
# EMAIL CONFIGURATION
# --------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@crm.example.com")

# --------------------------------------------------
# THIRD-PARTY APP SETTINGS
# --------------------------------------------------
# Frontend URL for invitation/reset links
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Stripe (payment links) -- billing views handle StripeNotConfigured
# gracefully rather than crashing when unset.
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Anthropic (AI content generation) -- ai_content views/tasks handle
# AIProviderNotConfigured gracefully rather than crashing when unset.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Stability AI (AI image/video generation) -- ai_content views/tasks
# handle ImageProviderNotConfigured gracefully rather than crashing.
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Jei naudoji reverse proxy / Nginx
USE_X_FORWARDED_HOST = True

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
# Console-only by default: Railway (and most PaaS) capture stdout/stderr
# directly, and a container's filesystem may not have the log directory
# a FileHandler would need. Set LOG_FILE to opt into logging to a file
# too (e.g. on a self-hosted box with a mounted volume for it).
LOG_FILE = os.getenv("LOG_FILE", "")

_log_handlers = ["console"]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": True,
        },
        "crm": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": True,
        },
        "celery": {
            "handlers": _log_handlers,
            "level": "INFO",
            "propagate": True,
        },
    },
    "root": {
        "handlers": _log_handlers,
        "level": "INFO",
    },
}

if LOG_FILE:
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    LOGGING["handlers"]["file"] = {
        "class": "logging.FileHandler",
        "filename": LOG_FILE,
        "formatter": "verbose",
    }
    _log_handlers.append("file")

# --------------------------------------------------
# ADDITIONAL PRODUCTION SETTINGS
# --------------------------------------------------

# Session settings
SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF settings
CSRF_COOKIE_AGE = 86400 * 7  # 7 days
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Security settings for file uploads
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Database connection settings
DATABASE_CONN_MAX_AGE = 600

# Email settings for production
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    # Fallback to console backend if SMTP not configured
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Sentry error tracking (optional)
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
                signals_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    )
