from django.conf import settings
from twilio.rest import Client


class TwilioNotConfigured(Exception):
    """Raised when the platform's TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN isn't set."""


def send_sms(to, body, from_number):
    """Send a single SMS via Twilio and return the created Message.

    `from_number` is the sending organization's own Twilio number (see
    Organization.twilio_from_number) -- never a number shared across
    tenants, so one organization's deliverability problems can't affect
    another's.

    Raises TwilioNotConfigured if the platform's Twilio credentials aren't
    set, so callers can log/skip instead of crashing on a raw Twilio/network
    exception.
    """
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN):
        raise TwilioNotConfigured(
            'TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN nenustatyti aplinkos kintamuosiuose.'
        )

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return client.messages.create(to=to, from_=from_number, body=body)
