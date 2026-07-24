import secrets

from src.core.config import get_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.authentication.application.commands import (
    PasswordResetRequestCommand,
)
from src.modules.authentication.application.ports import (
    EmailSenderPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.shared.application.ports import (
    CachePort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Initiates the password reset process.
Generates a cryptographically secure 32-byte URL-safe token, stores it in Redis
with a 15-minute TTL, and dispatches an email to the user with a reset link.
Fails silently if the email does not exist to prevent enumeration attacks.
"""


class PasswordResetRequestUseCase:
    """Handles generating a reset token and sending the email."""

    def __init__(
        self,
        uow: AuthUoWPort,
        cache: CachePort,
        email_sender: EmailSenderPort,
        frontend_url: str,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
    ):
        self.uow = uow
        self.cache = cache
        self.email_sender = email_sender
        self.frontend_url = frontend_url
        self.rate_limiter = rate_limiter
        self.turnstile = turnstile

    async def execute(self, command: PasswordResetRequestCommand) -> None:
        async with self.uow:
            limit_key = f"{command.client_meta.ip_address if command.client_meta else 'unknown'}:{command.email.lower()}"

            if command.is_challenged:
                if not command.turnstile_token:
                    await self.rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed(
                        "CAPTCHA challenge failed or missing"
                    )

                is_valid = await self.turnstile.verify_token(
                    command.turnstile_token,
                    command.client_meta.ip_address if command.client_meta else None,
                )
                if not is_valid:
                    await self.rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed("CAPTCHA verification failed")

            user = await self.uow.user_query_repo.find_by_email(
                command.email, project_id=command.project_id
            )
            if not user or not user.is_verified:
                # Silently return to prevent email enumeration attacks
                if command.is_challenged:
                    await self.rate_limiter.record_success(limit_key)
                return

            # Generate token
            token = secrets.token_urlsafe(32)

            # Store in cache with 15 minute TTL
            # Key: "pwd_reset:{token}" -> Value: user.id
            await self.cache.set_string(
                f"pwd_reset:{token}",
                str(user.id),
                get_settings().verification.PASSWORD_RESET_EXPIRY_SECONDS,
            )

            # Resolve frontend_url from project if applicable
            resolved_frontend_url = self.frontend_url
            if command.project_id:
                project = await self.uow.project_query_repo.get_by_id(
                    command.project_id
                )
                if project and project.frontend_url:
                    resolved_frontend_url = project.frontend_url.value

            base_url = resolved_frontend_url.rstrip("/")
            reset_url = f"{base_url}/reset-password?token={token}"
            await self.email_sender.send_password_reset_email(
                command.email,
                reset_url,
                tenant_id=user.id if not user.project_id else None,
                project_id=command.project_id,
            )

            if command.is_challenged:
                await self.rate_limiter.record_success(limit_key)
