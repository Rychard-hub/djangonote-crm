from django.conf import settings
from twilio.rest import Client


class TwilioNotConfigured(Exception):
    """Raised when TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM_NUMBER isn't set."""


def send_sms(to, body):
    """Send a single SMS via Twilio and return the created Message.

    Raises TwilioNotConfigured if Twilio credentials aren't set, so callers
    can log/skip instead of crashing on a raw Twilio/network exception.
    """
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
        raise TwilioNotConfigured(
            'TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM_NUMBER nenustatyti aplinkos kintamuosiuose.'
        )

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return client.messages.create(to=to, from_=settings.TWILIO_FROM_NUMBER, body=body)
