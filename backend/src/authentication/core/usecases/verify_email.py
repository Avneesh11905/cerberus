"""
Validates a short-lived 6-digit OTP sent to the user's email during registration.
If the OTP matches the one stored in the ephemeral cache (Redis), the user
is permanently marked as verified in the database, and the Welcome Email is dispatched.
"""

import hashlib
import time
from uuid import UUID

from src.authentication.core.domain import UserIdentity
from src.authentication.core.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from src.authentication.core.domain.session import ClientMetadata
from src.authentication.core.ports import RefreshTokenRepositoryPort, UserRepositoryPort
from src.authentication.core.ports.email_sender import EmailSenderPort
from src.authentication.core.utils import anonymize_email, verify_otp_hash
from src.shared.config import verification_settings
from src.shared.core.ports.cache import CachePort
from src.shared.core.ports.logger import LoggerPort
from src.shared.core.ports.uow import UoWPort


class VerifyEmailUseCase[SessionType]:
    """Handles verification of the 6-digit OTP for email verification."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        cache: CachePort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        refresh_repo: RefreshTokenRepositoryPort,
    ):
        self._user_repo = user_repo

        self._cache = cache
        self._logger = logger
        self._email_sender = email_sender
        self._refresh_repo = refresh_repo

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        otp: str,
        client_meta: ClientMetadata | None = None,
        project_id: UUID | None = None,
    ) -> tuple[UserIdentity, str]:
        """
        Verifies the OTP for the given email using the Redis-First flow.
        If valid, saves the user to the DB and sends welcome email.
        Raises Domain Exceptions if invalid or expired.
        """

        # 1. Check if user is in DB
        user = await self._user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if not user:
            await self._logger.warning(
                f"Verification failed: User {anonymize_email(email)} not found"
            )
            raise InvalidCredentialsException()

        if user.is_verified:
            await self._logger.warning(
                f"Verification failed: User {anonymize_email(email)} is already verified"
            )
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
            raise InvalidTokenException()

        # 3. Fetch pending registration payload from Redis
        payload = await self._cache.get_dict(redis_key)

        if not payload:
            await self._logger.warning(
                f"Verification failed: No pending registration found for {anonymize_email(email)}"
            )
            raise InvalidTokenException()

        # 4. Check 5-minute expiry
        current_time = int(time.time())
        otp_expires_at = int(payload.get("otp_expires_at", 0))
        if current_time > otp_expires_at:
            await self._logger.warning(
                f"Verification failed: OTP expired for {anonymize_email(email)}"
            )
            raise InvalidTokenException()

        # 5. Compare OTP securely
        stored_otp_hash = str(payload.get("otp", ""))
        provided_otp = str(otp)

        if not verify_otp_hash(provided_otp, stored_otp_hash):
            await self._logger.warning(
                f"Verification failed: Incorrect OTP for {anonymize_email(email)}"
            )
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
        return user, token
