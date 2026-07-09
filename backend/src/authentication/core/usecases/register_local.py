"""
Orchestrates the local registration flow.
Responsible for checking email uniqueness, hashing the user's password,
persisting the new user, and triggering the OTP email verification process.
The user is created immediately but flagged as is_verified=False until OTP succeeds.
"""

import hashlib
import secrets
import time
from uuid import UUID

from src.authentication.core.domain import EmailAlreadyRegisteredException, UserRole
from src.authentication.core.ports import PasswordHasherPort, UserRepositoryPort
from src.authentication.core.ports.email_sender import EmailSenderPort
from src.authentication.core.utils import anonymize_email, hash_otp
from src.shared.config import app_settings, verification_settings
from src.shared.core.ports.cache import CachePort
from src.shared.core.ports.logger import LoggerPort
from src.shared.core.ports.uow import UoWPort


class RegisterLocalUserUseCase[SessionType]:
    """Handles user registration with email and password."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        cache: CachePort,
    ):
        self._user_repo = user_repo

        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._cache = cache

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        password: str,
        name: str | None,
        project_id: UUID | None = None,
        role: UserRole = UserRole.USER,
    ) -> None:
        """
        Register a new user and trigger email verification.
        Saves the pending registration data to Redis (Redis-First Flow).
        Raises ValueError if email already exists in DB.
        """
        if project_id is not None:
            role = UserRole.USER

        if (
            app_settings.ADMIN_EMAIL
            and email.strip().lower() == app_settings.ADMIN_EMAIL.strip().lower()
            and project_id is None
        ):
            role = UserRole.ADMIN

        # 1. Check if email exists in PostgreSQL
        existing = await self._user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if existing and existing.is_verified:
            await self._logger.warning(
                f"Registration failed: Email {anonymize_email(email)} already registered and verified"
            )
            raise EmailAlreadyRegisteredException()

        # 2. Hash password securely
        hashed = await self._hasher.hash_password(password)

        if not existing:
            # 3a. Save pending user to PostgreSQL directly, but without a password.
            await self._user_repo.create_user_with_password(
                session=uow.session,
                email=email,
                name=name,
                password_hash=None,
                is_verified=False,
                project_id=project_id,
                role=role,
            )
        else:
            # 3b. DO NOT update password for unverified user here to prevent pre-hijacking.
            pass

        # 3. Generate 6-digit OTP and calculate 5-minute expiry
        otp = f"{secrets.randbelow(1000000):06d}"
        otp_expires_at = int(time.time()) + verification_settings.OTP_EXPIRATION_SECONDS

        # 4. Construct pending payload with HASHED OTP and the pending password
        payload = {
            "otp": hash_otp(otp),
            "otp_expires_at": otp_expires_at,
            "pending_password_hash": hashed,
            "pending_name": name,
            "project_id": str(project_id) if project_id else None,
            "role": role.value,  # serialize enum to string — json.dumps cannot handle enum objects
        }

        # 5. Save OTP to Redis for 15 minutes (resend window)
        # Use project_id in cache key to avoid collisions between tenants for the same email
        email_hash = hashlib.sha256(email.encode()).hexdigest()
        cache_key = (
            f"pending_reg:{str(project_id)}:{email_hash}"
            if project_id
            else f"pending_reg:global:{email_hash}"
        )

        # Use SETNX to prevent race conditions when two concurrent registrations for the same email are submitted
        success = await self._cache.set_dict_nx(
            cache_key, payload, verification_settings.OTP_RESEND_WINDOW_SECONDS
        )
        if not success:
            await self._logger.warning(
                f"Registration failed: Concurrent registration attempt for {anonymize_email(email)}"
            )
            raise EmailAlreadyRegisteredException()

        # 6. Dispatch email
        await self._email_sender.send_verification_email(email, otp)

        await self._logger.info(
            f"Pending registration cached for {anonymize_email(email)}. Verification OTP sent."
        )
