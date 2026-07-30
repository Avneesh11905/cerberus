import hashlib
import secrets
import time

from src.core.config import get_settings
from src.core.exceptions import TurnstileVerificationFailed, RateLimitExceededException
from src.modules.authentication.application.commands import (
    LocalResendVerificationCommand,
)
from src.modules.authentication.application.ports import (
    EmailSenderPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.utils import hash_otp
from src.shared.application.ports import (
    CachePort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Allows unverified users to request a fresh 6-digit OTP if their previous one expired.
To prevent malicious actors from discovering which emails are registered, this usecase
fails silently (returns without error) if the email doesn't exist or is already verified.
"""


class LocalResendVerificationUseCase:
    """Handles requesting a new verification OTP."""

    def __init__(
        self,
        uow: AuthUoWPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        cache: CachePort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
    ):
        self.uow = uow
        self._logger = logger
        self._email_sender = email_sender
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile

    async def execute(self, command: LocalResendVerificationCommand) -> tuple[int, int]:
        async with self.uow:
            email_hash = hashlib.sha256(command.email.lower().encode()).hexdigest()
            scope = str(command.project_id) if command.project_id else "global"
            resend_key = f"otp_resends:{scope}:{email_hash}"
            limit_key = f"{command.client_meta.ip_address if command.client_meta else 'unknown'}:{command.email.lower()}"

            # Turnstile Verification (bypassed if project_id is present via API Key)
            if not command.project_id and command.is_challenged:
                if not command.turnstile_token:
                    await self._rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed(
                        "CAPTCHA challenge failed or missing"
                    )

                is_valid = await self._turnstile.verify_token(
                    command.turnstile_token,
                    command.client_meta.ip_address if command.client_meta else None,
                )
                if not is_valid:
                    await self._rate_limiter.record_failure(limit_key)
                    raise TurnstileVerificationFailed("CAPTCHA verification failed")

            expires_in = get_settings().verification.OTP_EXPIRATION_SECONDS
            cooldown_seconds = get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS

            cooldown_key = f"otp_cooldown:{scope}:{email_hash}"
            is_cooling_down = await self._cache.get_dict(cooldown_key)
            if is_cooling_down:
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                    await self._rate_limiter.record_failure(limit_key)
                raise RateLimitExceededException(
                    "Please wait before requesting another code.",
                    retry_after=cooldown_seconds,
                )

            # Check user existence and verification status FIRST.
            # The rate-limit counter is only bumped once we confirm the user exists,
            # so an attacker cannot exhaust a real user's resend quota by spamming
            # requests for arbitrary email addresses they don't control.
            user = await self.uow.user_query_repo.find_by_email(
                command.email, project_id=command.project_id
            )
            if not user:
                # Silently return to prevent email enumeration.
                if command.is_challenged:
                    await self._rate_limiter.record_success(limit_key)
                return (
                    expires_in,
                    get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS,
                )

            if user.is_verified:
                # Silently return to prevent email enumeration.
                if command.is_challenged:
                    await self._rate_limiter.record_success(limit_key)
                return (
                    expires_in,
                    get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS,
                )

            # Increment the counter now that the user is verified as eligible.
            resends = await self._cache.incr(resend_key, ttl=3600)
            if resends > 3:
                await self._logger.warning("OTP resend rate limit exceeded")
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                    await self._rate_limiter.record_failure(limit_key)
                return (
                    expires_in,
                    get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS,
                )

            redis_key = (
                f"pending_reg:{str(command.project_id)}:{email_hash}"
                if command.project_id
                else f"pending_reg:global:{email_hash}"
            )

            existing_payload = await self._cache.get_dict(redis_key)
            if not existing_payload:
                # The pending registration expired. User must register again.
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                    await self._rate_limiter.record_failure(limit_key)
                return (
                    expires_in,
                    get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS,
                )

            otp = f"{secrets.randbelow(1000000):06d}"
            otp_expires_at = (
                int(time.time()) + get_settings().verification.OTP_EXPIRATION_SECONDS
            )

            payload = {
                "otp": hash_otp(otp),
                "otp_expires_at": otp_expires_at,
                "pending_password_hash": existing_payload.get("pending_password_hash"),
                "pending_name": existing_payload.get("pending_name"),
                "attempts": 0,
            }

            # Save to Redis, refreshing the 15 minute total TTL
            await self._cache.set_dict(
                redis_key,
                payload,
                get_settings().verification.OTP_RESEND_WINDOW_SECONDS,
            )

            await self._cache.set_dict(
                cooldown_key,
                {"cooling_down": True},
                cooldown_seconds,
            )

            # Reset the attempt counter atomically
            attempt_key = f"otp_attempts:{scope}:{email_hash}"
            await self._cache.delete_key(attempt_key)

            await self._email_sender.send_verification_email(
                command.email,
                otp,
                project_id=command.project_id,
            )
            await self._logger.info(
                f"Resent verification OTP to pending user {command.email}"
            )

            if command.is_challenged:
                await self._rate_limiter.record_success(limit_key)

            return expires_in, get_settings().verification.OTP_RESEND_COOLDOWN_SECONDS
