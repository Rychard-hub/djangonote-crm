import time

import anthropic
import requests
from django.conf import settings
from django.utils import timezone

MODEL = 'claude-opus-5'

# Stability AI (image + video generation). Chosen provider for
# docs/bussynote-mvp-architecture.md section 6's image/video step.
STABILITY_API_BASE = 'https://api.stability.ai'
STABILITY_IMAGE_MODEL = 'core'  # v2beta/stable-image/generate/core
VIDEO_POLL_INTERVAL_SECONDS = 10
VIDEO_POLL_TIMEOUT_SECONDS = 600

PROMPT_TEMPLATES = {
    'script': 'Parašyk trumpą (iki 150 žodžių) rinkodaros scenarijų remiantis šiuo aprašymu:\n\n{prompt}',
    'headline': (
        'Sugalvok 5 trumpas, patrauklias rinkodaros antraštes remiantis šiuo '
        'aprašymu. Pateik jas kaip sunumeruotą sąrašą:\n\n{prompt}'
    ),
}


class AIProviderNotConfigured(Exception):
    """Raised when ANTHROPIC_API_KEY isn't set."""


class ImageProviderNotConfigured(Exception):
    """Raised when STABILITY_API_KEY isn't set."""


class GenerationFailed(Exception):
    """Raised when Stability AI returns a non-success response."""


def generate_text(kind, prompt):
    """Call Claude to generate marketing text for a ContentJob's kind + prompt."""
    if not settings.ANTHROPIC_API_KEY:
        raise AIProviderNotConfigured('ANTHROPIC_API_KEY nenustatytas aplinkos kintamuosiuose.')

    template = PROMPT_TEMPLATES.get(kind, '{prompt}')
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{'role': 'user', 'content': template.format(prompt=prompt)}],
    )
    return next((block.text for block in response.content if block.type == 'text'), '')


def content_jobs_remaining(subscription):
    """AI content generations left this month for this subscription's plan.

    Unlike Subscription.payment_links_remaining() (billing app, 0 = unlimited),
    this lives here rather than as a Subscription method because it queries
    ContentJob, which billing can't import without inverting the dependency
    direction (ai_content depends on billing, not the other way around).
    0 here just means zero -- has_feature('ai_content') is what actually
    keeps the Free plan out, so no plan is expected to reach this with a
    quota of 0 while also having the feature enabled.
    """
    from .models import ContentJob

    quota = subscription.plan.ai_content_quota
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = ContentJob.objects.filter(
        organization=subscription.organization, created_at__gte=month_start,
    ).exclude(status='failed').count()
    return max(quota - used, 0)


def _stability_headers(accept):
    if not settings.STABILITY_API_KEY:
        raise ImageProviderNotConfigured('STABILITY_API_KEY nenustatytas aplinkos kintamuosiuose.')
    return {'authorization': f'Bearer {settings.STABILITY_API_KEY}', 'accept': accept}


def generate_image_bytes(prompt):
    """Call Stability AI text-to-image. Returns (bytes, content_type)."""
    response = requests.post(
        f'{STABILITY_API_BASE}/v2beta/stable-image/generate/{STABILITY_IMAGE_MODEL}',
        headers=_stability_headers('image/*'),
        files={'none': ''},  # forces multipart/form-data even with no file field
        data={'prompt': prompt, 'output_format': 'png'},
        timeout=60,
    )
    if response.status_code != 200:
        raise GenerationFailed(f'Stability AI vaizdo generavimo klaida ({response.status_code}): {response.text[:300]}')
    return response.content, 'image/png'


def generate_video_bytes(prompt):
    """Generate a short video from a text prompt via Stability AI.

    Stability has no single-call text-to-video endpoint -- only
    image-to-video. So this generates a keyframe image from the prompt
    first, then animates it, polling until the async job finishes.
    """
    image_bytes, _ = generate_image_bytes(prompt)

    start_response = requests.post(
        f'{STABILITY_API_BASE}/v2beta/image-to-video',
        headers=_stability_headers('application/json'),
        files={'image': ('keyframe.png', image_bytes, 'image/png')},
        data={'seed': 0, 'cfg_scale': 1.8, 'motion_bucket_id': 127},
        timeout=60,
    )
    if start_response.status_code != 200:
        raise GenerationFailed(
            f'Stability AI video generavimo pradžios klaida ({start_response.status_code}): {start_response.text[:300]}'
        )
    generation_id = start_response.json()['id']

    deadline = time.monotonic() + VIDEO_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        result_response = requests.get(
            f'{STABILITY_API_BASE}/v2beta/image-to-video/result/{generation_id}',
            headers=_stability_headers('video/*'),
            timeout=30,
        )
        if result_response.status_code == 202:
            time.sleep(VIDEO_POLL_INTERVAL_SECONDS)
            continue
        if result_response.status_code != 200:
            raise GenerationFailed(
                f'Stability AI video rezultato klaida ({result_response.status_code}): {result_response.text[:300]}'
            )
        return result_response.content, 'video/mp4'

    raise GenerationFailed('Stability AI video generavimas neužsibaigė per nustatytą laiką.')
