"""
Validates a short-lived 6-digit OTP sent to the user's email during registration.
If the OTP matches the one stored in the ephemeral cache (Redis), the user
is permanently marked as verified in the database, and the Welcome Email is dispatched.
"""

import hashlib
import time
from uuid import UUID

from src.core.config import verification_settings
from src.core.exceptions import RateLimitExceededException, TurnstileVerificationFailed
from src.modules.auth.application.ports import (
    RefreshTokenRepositoryPort,
    UserRepositoryPort,
)
from src.modules.auth.application.ports.email_sender import EmailSenderPort
from src.modules.auth.application.utils import anonymize_email, verify_otp_hash
from src.modules.auth.domain import UserIdentity
from src.modules.auth.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from src.modules.auth.domain.session import ClientMetadata
from src.shared.application.ports.analytics import AnalyticsEventPort
from src.shared.application.ports.cache import CachePort
from src.shared.application.ports.logger import LoggerPort
from src.shared.application.ports.rate_limiter import RateLimiterPort
from src.shared.application.ports.turnstile import TurnstilePort
from src.shared.application.ports.uow import UoWPort


class VerifyEmailUseCase[SessionType]:
    """Handles verification of the 6-digit OTP for email verification."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        cache: CachePort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        refresh_repo: RefreshTokenRepositoryPort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
    ):
        self._user_repo = user_repo
        self._cache = cache
        self._logger = logger
        self._email_sender = email_sender
        self._refresh_repo = refresh_repo
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        otp: str,
        client_meta: ClientMetadata | None = None,
        project_id: UUID | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> tuple[UserIdentity, str]:
        """
        Verifies the OTP for the given email using the Redis-First flow.
        If valid, saves the user to the DB and sends welcome email.
        Raises Domain Exceptions if invalid or expired.
        """
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

        # 1. Check if user is in DB
        user = await self._user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if not user:
            await self._logger.warning(
                f"Verification failed: User {anonymize_email(email)} not found"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise InvalidCredentialsException()

        if user.is_verified:
            await self._logger.warning(
                f"Verification failed: User {anonymize_email(email)} is already verified"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise InvalidCredentialsException()

        # 2. Increment attempt count atomically using the dedicated counter key
        email_hash = hashlib.sha256(email.encode()).hexdigest()
        scope = str(project_id) if project_id else "global"
        attempt_key = f"otp_attempts:{scope}:{email_hash}"
        redis_key = (
            f"pending_reg:{str(project_id)}:{email_hash}"
            if project_id
            else f"pending_reg:global:{email_hash}"
        )

        exceeded = await self._cache.increment_and_check_exceeds(
            attempt_key,
            redis_key,
            verification_settings.OTP_RESEND_WINDOW_SECONDS,
            verification_settings.OTP_MAX_ATTEMPTS,
        )

        if exceeded:
            await self._logger.warning(
                f"Verification failed: Too many OTP attempts for {anonymize_email(email)}"
            )
            self._analytics.record_event(
                project_id=project_id,
                event_type="OTP_ABUSE_ATTEMPT",
                user_id=user.id,
                metadata=client_meta.model_dump() if client_meta else None,
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise RateLimitExceededException("Too many verification attempts")

        # 3. Fetch pending registration payload from Redis
        payload = await self._cache.get_dict(redis_key)

        if not payload:
            await self._logger.warning(
                f"Verification failed: No pending registration found for {anonymize_email(email)}"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise InvalidTokenException()

        # 4. Check 5-minute expiry
        current_time = int(time.time())
        otp_expires_at = int(payload.get("otp_expires_at", 0))
        if current_time > otp_expires_at:
            await self._logger.warning(
                f"Verification failed: OTP expired for {anonymize_email(email)}"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise InvalidTokenException()

        # 5. Compare OTP securely
        stored_otp_hash = str(payload.get("otp", ""))
        provided_otp = str(otp)

        if not verify_otp_hash(provided_otp, stored_otp_hash):
            await self._logger.warning(
                f"Verification failed: Incorrect OTP for {anonymize_email(email)}"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            raise InvalidTokenException()

        # 6. Success! Mark the user as verified in PostgreSQL
        await self._user_repo.verify_user_email(
            uow.session, user.id, name=payload.get("pending_name")
        )

        pending_password_hash = payload.get("pending_password_hash")
        if pending_password_hash:
            await self._user_repo.update_password(
                uow.session, user.id, pending_password_hash
            )

        # Issue a refresh token to auto-login
        token = await self._refresh_repo.create(
            uow.session, user.id, client_meta=client_meta
        )

        await uow.session.flush()  # type: ignore

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
        await self._email_sender.send_welcome_email(user.email, user.name)

        await self._logger.info(f"User {user.id} email verified successfully")

        self._analytics.record_event(
            project_id=project_id,
            tenant_id=user.id if not project_id else None,
            event_type="REGISTRATION",
            user_id=user.id if project_id else None,
            metadata=client_meta.model_dump() if client_meta else None,
        )

        if is_challenged:
            await self._rate_limiter.record_success(limit_key)

        return user, token
