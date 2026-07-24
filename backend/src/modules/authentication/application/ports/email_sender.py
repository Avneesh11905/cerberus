"""
Port: Email Sender (Authentication Domain)

Defines the interface for sending auth-specific transactional emails.
Each domain defines its own email sender port with domain-specific methods.
"""

from typing import Protocol
from uuid import UUID


class EmailSenderPort(Protocol):
    """Interface for sending authentication transactional emails."""

    async def send_welcome_email(
        self,
        to_email: str,
        name: str | None,
        tenant_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> None:
        """Send a welcome email to a newly registered user."""
        ...

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_url: str,
        tenant_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> None:
        """Send a password reset email."""
        ...

    async def send_verification_email(
        self,
        to_email: str,
        otp: str,
        tenant_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> None:
        """Send an email address verification email containing a 6-digit OTP."""
        ...

    async def send_account_restored_email(
        self,
        to_email: str,
        name: str | None,
        tenant_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> None:
        """Send an email notifying the user that their account has been restored."""
        ...

    async def send_login_detected_email(
        self,
        to_email: str,
        ip_address: str,
        device_info: str,
        tenant_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> None:
        """Send an email notifying the user of a login from a new device or IP address."""
        ...
