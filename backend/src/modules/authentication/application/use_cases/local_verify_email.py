import dataclasses
import hashlib
import time

from src.core.config import get_settings
from src.core.exceptions import RateLimitExceededException, TurnstileVerificationFailed
from src.modules.authentication.application.commands import LocalVerifyEmailCommand
from src.modules.authentication.application.ports import (
    EmailSenderPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.utils import (
    anonymize_email,
    verify_otp_hash,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from src.shared.application.ports import (
    AnalyticsEventPort,
    CachePort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Validates a short-lived 6-digit OTP sent to the user's email during registration.
If the OTP matches the one stored in the ephemeral cache (Redis), the user
is permanently marked as verified in the database, and the Welcome Email is dispatched.
"""


class LocalVerifyEmailUseCase:
    """Handles verification of the 6-digit OTP for email verification."""

    def __init__(
        self,
        uow: AuthUoWPort,
        cache: CachePort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
    ):
        self.uow = uow
        self._cache = cache
        self._logger = logger
        self._email_sender = email_sender
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics

    async def execute(
        self, command: LocalVerifyEmailCommand
    ) -> tuple[UserIdentity, str]:
        async with self.uow:
            """
        Verifies the OTP for the given email using the Redis-First flow.
        If valid, saves the user to the DB and sends welcome email.
        Raises Domain Exceptions if invalid or expired.
        """
            limit_key = f"{command.client_meta.ip_address if command.client_meta else 'unknown'}:{command.email.lower()}"

            if command.is_challenged:
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

            # 1. Check if user is in DB
            user = await self.uow.user_query_repo.find_by_email(
                command.email, project_id=command.project_id
            )
            if not user:
                await self._logger.warning(
                    f"Verification failed: User {anonymize_email(command.email)} not found"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise InvalidCredentialsException()

            if user.is_verified:
                await self._logger.warning(
                    f"Verification failed: User {anonymize_email(command.email)} is already verified"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise InvalidCredentialsException()

            # 2. Increment attempt count atomically using the dedicated counter key
            email_hash = hashlib.sha256(command.email.encode()).hexdigest()
            scope = str(command.project_id) if command.project_id else "global"
            attempt_key = f"otp_attempts:{scope}:{email_hash}"
            redis_key = (
                f"pending_reg:{str(command.project_id)}:{email_hash}"
                if command.project_id
                else f"pending_reg:global:{email_hash}"
            )

            exceeded = await self._cache.increment_and_check_exceeds(
                attempt_key,
                redis_key,
                get_settings().verification.OTP_RESEND_WINDOW_SECONDS,
                get_settings().verification.OTP_MAX_ATTEMPTS,
            )

            if exceeded:
                await self._logger.warning(
                    f"Verification failed: Too many OTP attempts for {anonymize_email(command.email)}"
                )
                self._analytics.record_event(
                    project_id=command.project_id,
                    event_type="OTP_ABUSE_ATTEMPT",
                    user_id=user.id,
                    metadata=dataclasses.asdict(command.client_meta)
                    if command.client_meta
                    else None,
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise RateLimitExceededException("Too many verification attempts")

            # 3. Fetch pending registration payload from Redis
            payload = await self._cache.get_dict(redis_key)

            if not payload:
                await self._logger.warning(
                    f"Verification failed: No pending registration found for {anonymize_email(command.email)}"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise InvalidTokenException()

            # 4. Check 5-minute expiry
            current_time = int(time.time())
            otp_expires_at = int(payload.get("otp_expires_at", 0))
            if current_time > otp_expires_at:
                await self._logger.warning(
                    f"Verification failed: OTP expired for {anonymize_email(command.email)}"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise InvalidTokenException()

            # 5. Compare OTP securely
            stored_otp_hash = str(payload.get("otp", ""))
            provided_otp = str(command.otp)

            if not verify_otp_hash(provided_otp, stored_otp_hash):
                await self._logger.warning(
                    f"Verification failed: Incorrect OTP for {anonymize_email(command.email)}"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                raise InvalidTokenException()

            # 6. Success! Mark the user as verified in PostgreSQL
            await self.uow.user_command_repo.verify_user_email(
                user.id, name=payload.get("pending_name")
            )

            pending_password_hash = payload.get("pending_password_hash")
            if pending_password_hash:
                await self.uow.user_command_repo.update_password(
                    user.id, pending_password_hash
                )

            # Issue a refresh token to auto-login
            token = await self.uow.refresh_token_repo.create(
                user.id, client_meta=command.client_meta
            )

            await self.uow.session.flush()
            # Clean up Redis (registration payload and attempts counter).
            # This runs before the UoW commit completes. If the commit later fails the
            # DB rolls back, but these Redis keys are already gone. The user will need
            # to re-register — acceptable since they're within the OTP resend window.
            # Wrapped in try/except so a transient Redis error does not block verification.
            try:
                await self._cache.delete_key(redis_key)
                await self._cache.delete_key(attempt_key)
            except Exception:
                await self._logger.warning(
                    "Redis cleanup after email verification failed — keys will expire naturally via TTL"
                )

            # Send the welcome email
            await self._email_sender.send_welcome_email(user.email.value, user.name)

            await self._logger.info(f"User {user.id} email verified successfully")

            self._analytics.record_event(
                project_id=command.project_id,
                tenant_id=user.id if not command.project_id else None,
                event_type="REGISTRATION",
                user_id=user.id if command.project_id else None,
                metadata=dataclasses.asdict(command.client_meta)
                if command.client_meta
                else None,
            )

            if command.is_challenged:
                await self._rate_limiter.record_success(limit_key)

            return user, token
