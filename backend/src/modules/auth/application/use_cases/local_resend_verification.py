"""
Allows unverified users to request a fresh 6-digit OTP if their previous one expired.
To prevent malicious actors from discovering which emails are registered, this usecase
fails silently (returns without error) if the email doesn't exist or is already verified.
"""

import hashlib
import secrets
import time
from uuid import UUID

from src.core.config import verification_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.auth.application.ports import UserQueryRepositoryPort, EmailSenderPort
from src.modules.auth.application.utils import hash_otp
from src.shared.domain.entities import ClientMetadata
from src.shared.application.ports import (
    CachePort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
    UoWPort,
)


class LocalResendVerificationUseCase[SessionType]:
    """Handles requesting a new verification OTP."""

    def __init__(
        self,
        user_query_repo: UserQueryRepositoryPort[SessionType],
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        cache: CachePort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
    ):
        self._user_query_repo = user_query_repo
        self._logger = logger
        self._email_sender = email_sender
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        project_id: UUID | None = None,
        client_meta: ClientMetadata | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> int:
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
        scope = str(project_id) if project_id else "global"
        resend_key = f"otp_resends:{scope}:{email_hash}"
        limit_key = (
            f"{client_meta.ip_address if client_meta else 'unknown'}:{email.lower()}"
        )

        if is_challenged:
            if not turnstile_token:
                await self._rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA challenge failed or missing")

            is_valid = await self._turnstile.verify_token(
                turnstile_token, client_meta.ip_address if client_meta else None
            )
            if not is_valid:
                await self._rate_limiter.record_failure(limit_key)
                raise TurnstileVerificationFailed("CAPTCHA verification failed")

        expires_in = verification_settings.OTP_EXPIRATION_SECONDS

        # Check user existence and verification status FIRST.
        # The rate-limit counter is only bumped once we confirm the user exists,
        # so an attacker cannot exhaust a real user's resend quota by spamming
        # requests for arbitrary email addresses they don't control.
        user = await self._user_query_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if not user:
            # Silently return to prevent email enumeration.
            if is_challenged:
                await self._rate_limiter.record_success(limit_key)
            return expires_in

        if user.is_verified:
            # Silently return to prevent email enumeration.
            if is_challenged:
                await self._rate_limiter.record_success(limit_key)
            return expires_in

        # Increment the counter now that the user is verified as eligible.
        resends = await self._cache.incr(resend_key, ttl=3600)
        if resends > 3:
            await self._logger.warning("OTP resend rate limit exceeded")
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
            return expires_in

        redis_key = (
            f"pending_reg:{str(project_id)}:{email_hash}"
            if project_id
            else f"pending_reg:global:{email_hash}"
        )

        existing_payload = await self._cache.get_dict(redis_key)
        if not existing_payload:
            # The pending registration expired. User must register again.
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
            return expires_in

        otp = f"{secrets.randbelow(1000000):06d}"
        otp_expires_at = int(time.time()) + verification_settings.OTP_EXPIRATION_SECONDS

        payload = {
            "otp": hash_otp(otp),
            "otp_expires_at": otp_expires_at,
            "pending_password_hash": existing_payload.get("pending_password_hash"),
            "pending_name": existing_payload.get("pending_name"),
            "attempts": 0,
        }

        # Save to Redis, refreshing the 15 minute total TTL
        await self._cache.set_dict(
            redis_key, payload, verification_settings.OTP_RESEND_WINDOW_SECONDS
        )

        # Reset the attempt counter atomically
        attempt_key = f"otp_attempts:{scope}:{email_hash}"
        await self._cache.delete_key(attempt_key)

        await self._email_sender.send_verification_email(email, otp)
        await self._logger.info(f"Resent verification OTP to pending user {email}")

        if is_challenged:
            await self._rate_limiter.record_success(limit_key)

        return expires_in
