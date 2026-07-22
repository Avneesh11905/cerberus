"""
Adapter: Resend Email Client

Implements SharedEmailClientPort using the Resend API.
This is the ONLY file that needs to change when swapping the email provider.
To swap to SendGrid, create src/shared/adapters/sendgrid_email_client.py and
implement the same SharedEmailClientPort interface.
"""

import smtplib
from email.message import EmailMessage

import resend

from src.shared.application.ports import SharedEmailClientPort


class ResendEmailClientAdapter(SharedEmailClientPort):
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


class SMTPEmailClientAdapter(SharedEmailClientPort):
    def __init__(
        self, smtp_host: str, smtp_port: int, from_email: str, reply_to: str | None
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self._from_email = from_email
        self._reply_to = reply_to

    def send_email(self, to: str, subject: str, html: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._from_email
        msg["To"] = to
        msg.set_content("Please view this email in an HTML-compatible client.")
        msg.add_alternative(html, subtype="html")
        if self._reply_to:
            msg["Reply-To"] = self._reply_to

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.send_message(msg)
