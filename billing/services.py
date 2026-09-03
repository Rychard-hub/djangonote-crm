import stripe
from django.conf import settings

DEFAULT_PLAN_CODE = 'free'


class StripeNotConfigured(Exception):
    """Raised when STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET isn't set."""


def get_subscription(organization):
    """Resolve the Subscription for an Organization, provisioning a free one if missing.

    Mirrors accounts.get_organization()'s self-healing: an Organization
    created before billing existed (or via a path that skips subscription
    setup) still needs to resolve to *some* plan rather than crashing every
    view that checks quotas or has_feature().
    """
    from .models import Plan, Subscription

    subscription = Subscription.objects.filter(organization=organization).select_related('plan').first()
    if subscription is not None:
        return subscription

    plan, _ = Plan.objects.get_or_create(
        code=DEFAULT_PLAN_CODE,
        defaults={'name': 'Free', 'monthly_price': 0, 'max_payment_links_per_month': 3},
    )
    return Subscription.objects.create(organization=organization, plan=plan)


def create_checkout_session(payment_link, success_url, cancel_url):
    """Create a Stripe Checkout Session for a not-yet-saved PaymentLink and return it.

    Raises StripeNotConfigured if no API key is set, so callers can show a
    clear message instead of a raw Stripe/network exception.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise StripeNotConfigured('STRIPE_SECRET_KEY nenustatytas aplinkos kintamuosiuose.')

    return stripe.checkout.Session.create(
        api_key=settings.STRIPE_SECRET_KEY,
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': payment_link.currency.lower(),
                'product_data': {'name': payment_link.description or 'Mokėjimas'},
                'unit_amount': int(payment_link.amount * 100),
            },
            'quantity': 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'organization_id': str(payment_link.organization_id)},
    )


def create_subscription_checkout_session(organization, plan, success_url, cancel_url):
    """Create a Stripe Checkout Session that starts a recurring subscription to `plan`."""
    if not settings.STRIPE_SECRET_KEY:
        raise StripeNotConfigured('STRIPE_SECRET_KEY nenustatytas aplinkos kintamuosiuose.')
    if not plan.stripe_price_id:
        raise StripeNotConfigured(f'Planas „{plan.name}“ neturi priskirto stripe_price_id.')

    return stripe.checkout.Session.create(
        api_key=settings.STRIPE_SECRET_KEY,
        mode='subscription',
        line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'organization_id': str(organization.pk), 'plan_code': plan.code},
    )


def verify_webhook_event(payload, sig_header):
    """Verify and parse an incoming Stripe webhook payload."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise StripeNotConfigured('STRIPE_WEBHOOK_SECRET nenustatytas aplinkos kintamuosiuose.')

    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
