import stripe
from django.conf import settings


class StripeNotConfigured(Exception):
    """Raised when STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET isn't set."""


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


def verify_webhook_event(payload, sig_header):
    """Verify and parse an incoming Stripe webhook payload."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise StripeNotConfigured('STRIPE_WEBHOOK_SECRET nenustatytas aplinkos kintamuosiuose.')

    return stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
