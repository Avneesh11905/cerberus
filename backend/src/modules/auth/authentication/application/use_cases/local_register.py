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

from src.shared.domain.entities import ClientMetadata

from src.core.config import verification_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.auth.authorization.application.services.role_provisioning import (
    RoleProvisioningService,
)
from src.modules.auth.authentication.application.ports import (
    PasswordHasherPort,
    UserQueryRepositoryPort,
    UserCommandRepositoryPort,
    EmailSenderPort,
)
from src.modules.auth.authentication.application.utils import anonymize_email, hash_otp
from src.shared.application.ports import (
    AnalyticsEventPort,
    CachePort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
    UoWPort,
)


class LocalRegisterUseCase[SessionType]:
    """Handles user registration with email and password."""

    def __init__(
        self,
        user_query_repo: UserQueryRepositoryPort,
        user_command_repo: UserCommandRepositoryPort,
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        cache: CachePort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
        role_provisioning: RoleProvisioningService[SessionType],
    ):
        self._user_query_repo = user_query_repo
        self._user_command_repo = user_command_repo
        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics
        self._role_provisioning = role_provisioning

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        password: str,
        name: str | None,
        project_id: UUID | None = None,
        client_meta: ClientMetadata | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> int:
        """
        Register a new user and trigger email verification.
        Saves the pending registration data to Redis (Redis-First Flow).
        Raises ValueError if email already exists in DB.
        """
        # Resolve role type based on context using the injected Authorization service
        role = await self._role_provisioning.determine_default_role(
            uow.session, email, project_id
        )

        # Rate limiting key
        limit_key = (
            f"{client_meta.ip_address if client_meta else 'unknown'}:{email.lower()}"
        )

        # Turnstile Verification
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

        # 1. Check if email exists in PostgreSQL
        existing = await self._user_query_repo.find_by_email(
            uow.session, email, project_id=project_id
        )

        # We compute the OTP expiry first so we can return it regardless of whether we fabricated or not
        otp_expires_at = int(time.time()) + verification_settings.OTP_EXPIRATION_SECONDS
        expires_in = verification_settings.OTP_EXPIRATION_SECONDS

        if existing and existing.is_verified:
            await self._logger.warning(
                f"Registration failed: Email {anonymize_email(email)} already registered and verified"
            )
            # Enumeration protection: silently dispatch a different email and pretend OTP was sent
            if is_challenged:
                await self._rate_limiter.record_success(limit_key)
            # TODO: Add logic to send "Account already exists" email if desired
            return expires_in

        # 2. Hash password securely
        hashed = await self._hasher.hash_password(password)

        if not existing:
            # 3a. Save pending user to PostgreSQL directly, but without a password.
            await self._user_command_repo.create_user_with_password(
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

        # 3. Generate 6-digit OTP
        otp = f"{secrets.randbelow(1000000):06d}"

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
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
            return expires_in  # enumeration protection

        if is_challenged:
            await self._rate_limiter.record_success(limit_key)

        # 6. Dispatch email
        await self._email_sender.send_verification_email(email, otp)

        await self._logger.info(
            f"Pending registration cached for {anonymize_email(email)}. Verification OTP sent."
        )

        # Analytics
        self._analytics.record_event(
            project_id=project_id,
            event_type="OTP_SENT",
            metadata=client_meta.model_dump() if client_meta else None,
        )

        return expires_in
