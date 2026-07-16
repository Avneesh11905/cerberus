"""
Adapter: Resend Email Client

Implements SharedEmailClientPort using the Resend API.
This is the ONLY file that needs to change when swapping the email provider.
To swap to SendGrid, create src/shared/adapters/sendgrid_email_client.py and
implement the same SharedEmailClientPort interface.
"""

import resend

from src.shared.application.ports.email_client import (
    SharedEmailClientPort,  # noqa: F401
)


class ResendEmailClient(SharedEmailClientPort):
    """Implements SharedEmailClientPort using the Resend transactional email API."""

    def __init__(self, api_key: str, from_email: str, reply_to: str | None) -> None:
        self._from_email = from_email
        self._reply_to = reply_to
        resend.api_key = api_key

    def send_email(self, to: str, subject: str, html: str) -> None:
        """Dispatch a pre-rendered HTML email via the Resend API."""
        params = {
            "from": self._from_email,
            "to": [to],
            "subject": subject,
            "html": html,
            "reply_to": self._reply_to,
        }
        resend.Emails.send(params)  # type: ignore
