import dataclasses
import hashlib
import secrets
import time

from src.core.config import get_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.authentication.application.commands import LocalRegisterCommand
from src.modules.authentication.application.ports import (
    EmailSenderPort,
    PasswordHasherPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.utils import anonymize_email, hash_otp
from src.modules.authorization.application.services.role_provisioning import (
    RoleProvisioningService,
)
from src.modules.authorization.domain.enums import GlobalRole
from src.shared.application.ports import (
    AnalyticsEventPort,
    CachePort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Orchestrates the local registration flow.
Responsible for checking email uniqueness, hashing the user's password,
persisting the new user, and triggering the OTP email verification process.
The user is created immediately but flagged as is_verified=False until OTP succeeds.
"""


class LocalRegisterUseCase:
    """Handles user registration with email and password."""

    def __init__(
        self,
        uow: AuthUoWPort,
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        cache: CachePort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
        role_provisioning: RoleProvisioningService,
    ):
        self.uow = uow
        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._cache = cache
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics
        self._role_provisioning = role_provisioning

    async def execute(self, command: LocalRegisterCommand) -> int:
        async with self.uow:
            """
        Register a new user and trigger email verification.
        Saves the pending registration data to Redis (Redis-First Flow).
        Raises ValueError if email already exists in DB.
        """
            # Resolve role type based on context using the injected Authorization service
            role = await self._role_provisioning.determine_default_role(
                email=command.email, project_id=command.project_id
            )

            # Rate limiting key
            limit_key = f"{command.client_meta.ip_address if command.client_meta else 'unknown'}:{command.email.lower()}"

            # Turnstile Verification
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

            # 1. Check if email exists in PostgreSQL
            existing = await self.uow.user_query_repo.find_by_email(
                command.email, project_id=command.project_id
            )

            # We compute the OTP expiry first so we can return it regardless of whether we fabricated or not
            otp_expires_at = (
                int(time.time()) + get_settings().verification.OTP_EXPIRATION_SECONDS
            )
            expires_in = get_settings().verification.OTP_EXPIRATION_SECONDS

            if existing and existing.is_verified:
                await self._logger.warning(
                    f"Registration failed: Email {anonymize_email(command.email)} already registered and verified"
                )
                # Enumeration protection: silently dispatch a different email and pretend OTP was sent
                if command.is_challenged:
                    await self._rate_limiter.record_success(limit_key)
                return expires_in

            # 2. Hash password securely
            hashed = await self._hasher.hash_password(command.password)

            if not existing:
                # 3a. Save pending user to PostgreSQL directly, but without a password.
                await self.uow.user_command_repo.create_user_with_password(
                    email=command.email,
                    name=command.name,
                    password_hash=None,
                    is_verified=False,
                    project_id=command.project_id,
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
                "pending_name": command.name,
                "project_id": str(command.project_id) if command.project_id else "",
                "role": role.value if isinstance(role, GlobalRole) else role,
            }

            # 5. Save OTP to Redis for 15 minutes (resend window)
            # Use project_id in cache key to avoid collisions between tenants for the same email
            email_hash = hashlib.sha256(command.email.encode()).hexdigest()
            cache_key = (
                f"pending_reg:{str(command.project_id)}:{email_hash}"
                if command.project_id
                else f"pending_reg:global:{email_hash}"
            )

            # Use SET instead of SETNX so that if a user closes the tab and tries to register again
            # within the 15-minute window, they will receive a new OTP. Turnstile prevents spam.
            await self._cache.set_dict(
                cache_key,
                payload,
                get_settings().verification.OTP_RESEND_WINDOW_SECONDS,
            )

            if command.is_challenged:
                await self._rate_limiter.record_success(limit_key)

            # 6. Dispatch email
            await self._email_sender.send_verification_email(
                command.email, 
                otp,
                project_id=command.project_id,
            )

            await self._logger.info(
                f"Pending registration cached for {anonymize_email(command.email)}. Verification OTP sent."
            )

            # Analytics
            self._analytics.record_event(
                project_id=command.project_id,
                event_type="OTP_SENT",
                metadata=dataclasses.asdict(command.client_meta)
                if command.client_meta
                else None,
            )

            return expires_in
