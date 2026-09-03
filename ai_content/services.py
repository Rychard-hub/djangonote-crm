import anthropic
from django.conf import settings
from django.utils import timezone

MODEL = 'claude-opus-5'

PROMPT_TEMPLATES = {
    'script': 'Parašyk trumpą (iki 150 žodžių) rinkodaros scenarijų remiantis šiuo aprašymu:\n\n{prompt}',
    'headline': (
        'Sugalvok 5 trumpas, patrauklias rinkodaros antraštes remiantis šiuo '
        'aprašymu. Pateik jas kaip sunumeruotą sąrašą:\n\n{prompt}'
    ),
}


class AIProviderNotConfigured(Exception):
    """Raised when ANTHROPIC_API_KEY isn't set."""


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
