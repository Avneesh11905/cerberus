"""
Initiates the password reset process.
Generates a cryptographically secure 32-byte URL-safe token, stores it in Redis
with a 15-minute TTL, and dispatches an email to the user with a reset link.
Fails silently if the email does not exist to prevent enumeration attacks.
"""

import secrets
from uuid import UUID

from src.core.config import verification_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.auth.application.ports import UserRepositoryPort
from src.modules.auth.application.ports.email_sender import EmailSenderPort
from src.shared.api.utils import ClientMetadata
from src.shared.application.ports.cache import CachePort
from src.shared.application.ports.rate_limiter import RateLimiterPort
from src.shared.application.ports.turnstile import TurnstilePort
from src.shared.application.ports.uow import UoWPort


class RequestPasswordResetUseCase[SessionType]:
    """Handles generating a reset token and sending the email."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        cache: CachePort,
        email_sender: EmailSenderPort,
        frontend_url: str,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
    ):
        self.user_repo = user_repo
        self.cache = cache
        self.email_sender = email_sender
        self.frontend_url = frontend_url
        self.rate_limiter = rate_limiter
        self.turnstile = turnstile

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        project_id: UUID | None = None,
        frontend_url: str | None = None,
        client_meta: ClientMetadata | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> None:
        limit_key = (
            f"{client_meta.ip_address if client_meta else 'unknown'}:{email.lower()}"
        )

        if is_challenged:
            if not turnstile_token:
                await self.rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA challenge failed or missing")

            is_valid = await self.turnstile.verify_token(
                turnstile_token, client_meta.ip_address if client_meta else None
            )
            if not is_valid:
                await self.rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA verification failed")

        user = await self.user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if not user or not user.is_verified:
            # Silently return to prevent email enumeration attacks
            if is_challenged:
                await self.rate_limiter.record_success(limit_key)
            return

        # Generate token
        token = secrets.token_urlsafe(32)

        # Store in cache with 15 minute TTL
        # Key: "pwd_reset:{token}" -> Value: user.id
        await self.cache.set_string(
            f"pwd_reset:{token}",
            str(user.id),
            verification_settings.PASSWORD_RESET_EXPIRY_SECONDS,
        )

        base_url = (frontend_url if frontend_url else self.frontend_url).rstrip("/")
        reset_url = f"{base_url}/reset-password?token={token}"
        await self.email_sender.send_password_reset_email(email, reset_url)

        if is_challenged:
            await self.rate_limiter.record_success(limit_key)
