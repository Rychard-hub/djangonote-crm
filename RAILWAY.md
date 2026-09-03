# Deploying to Railway

This app deploys to Railway as three services built from the same repo and
`Dockerfile`, plus two managed plugins:

- **Postgres** plugin (managed database)
- **Redis** plugin (Celery broker/result backend + Django cache)
- **web** service -- serves HTTP traffic (gunicorn)
- **worker** service -- runs Celery tasks (AI content generation, PDF
  generation, follow-up emails, ...)
- **beat** service -- fires the scheduled tasks in `CELERY_BEAT_SCHEDULE`
  (follow-up reminders, daily reports, cleanup)

File storage (generated images/videos/PDFs) goes to **Cloudflare R2**
rather than local disk, since Railway containers have an ephemeral
filesystem -- anything written to `MEDIA_ROOT` disappears on the next
deploy or restart otherwise.

## 1. Create the plugins

In your Railway project: **New -> Database -> PostgreSQL**, and
**New -> Database -> Redis**. Both inject `DATABASE_URL` / `REDIS_URL`
into every service in the project automatically -- nothing to copy by hand.

## 2. Create an R2 bucket

In the Cloudflare dashboard: R2 -> Create bucket. Then R2 -> Manage API
Tokens -> create a token with read/write access to that bucket. You'll get
an Account ID, Access Key ID, and Secret Access Key from this step.

Optional: enable the bucket's public access (R2 -> your bucket -> Settings
-> Public Access) or map a custom domain to it, and set
`AWS_S3_CUSTOM_DOMAIN` to that domain so media URLs are plain (unsigned).
Leave it unset to keep the bucket private and serve signed URLs instead.

## 3. Create the three services

All three point at this same GitHub repo/branch and use the root
`Dockerfile` (Railway auto-detects it; `railway.toml` pins it explicitly).
They differ only in their **Custom Start Command** (Settings -> Deploy ->
Custom Start Command on each service), taken from the `Procfile`:

| Service  | Custom Start Command |
|----------|-----------------------|
| web      | *(leave blank -- uses the Dockerfile's `CMD`)* |
| worker   | `celery -A crm_project worker --loglevel=info` |
| beat     | `celery -A crm_project beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler` |

Only the **web** service needs a public domain (Settings -> Networking ->
Generate Domain); worker/beat don't serve HTTP.

## 4. Run migrations

Railway supports a release-phase command per service (Settings -> Deploy
-> Release Command) on the **web** service:

```
python manage.py migrate --settings=crm_project.settings_production
```

(This is also documented as the `release:` line in `Procfile` for
platforms that read it directly.) Run it once by hand after the first
deploy too, via the Railway CLI or a one-off shell:

```
railway run python manage.py migrate --settings=crm_project.settings_production
railway run python manage.py createsuperuser --settings=crm_project.settings_production
```

## 5. Environment variables

Set these on **all three services** (Railway lets you share a variable
group across services, or paste the same values into each) -- see
`.env.example` for the full list with explanations:

- `DJANGO_SECRET_KEY` -- generate with
  `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DJANGO_ALLOWED_HOSTS` -- your web service's Railway domain (and any
  custom domain), e.g. `your-app.up.railway.app`
- `CSRF_TRUSTED_ORIGINS` -- same, but with the scheme, e.g.
  `https://your-app.up.railway.app`
- `FRONTEND_URL`
- `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
  `AWS_S3_ENDPOINT_URL`, `AWS_S3_REGION_NAME=auto`, and optionally
  `AWS_S3_CUSTOM_DOMAIN` -- from step 2
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
  (optional -- payment links/subscriptions degrade gracefully without them)
- `ANTHROPIC_API_KEY` (optional -- AI text generation degrades gracefully
  without it)
- `STABILITY_API_KEY` (optional -- AI image/video generation degrades
  gracefully without it)
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (optional --
  falls back to console/no-op email without them)

`DATABASE_URL` and `REDIS_URL` come from the plugins (step 1) -- don't set
those by hand. `PORT` is injected by Railway itself for the web service.

## 6. Stripe webhook

If using Stripe, point its webhook at
`https://<your-web-domain>/billing/webhook/` and put the signing secret in
`STRIPE_WEBHOOK_SECRET`.

## Local sanity check before deploying

```bash
docker build -t djangonote-crm .
docker run --rm -e DJANGO_SECRET_KEY=test -p 8000:8000 djangonote-crm
curl http://localhost:8000/api/health/
```

This won't have a real database/Redis behind it, so anything past the
health check will fail -- it's only meant to catch build-time errors
before pushing to Railway.
