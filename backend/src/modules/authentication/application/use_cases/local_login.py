import dataclasses
from datetime import datetime, timezone

from uuid6 import uuid7

from src.core.config import CoreSettings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.authentication.application.commands import LocalLoginCommand
from src.modules.authentication.application.ports import (
    AccessTokenPort,
    ClaimsProviderPort,
    EmailSenderPort,
    PasswordHasherPort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.utils import (
    anonymize_email,
    format_device_info,
)
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.domain.exceptions import (
    InvalidCredentialsException,
    UnverifiedEmailException,
)
from src.modules.authorization.domain.enums import GlobalRole
from src.shared.application.ports import (
    AnalyticsEventPort,
    LoggerPort,
    RateLimiterPort,
    TurnstilePort,
)

"""
Orchestrates the local authentication flow.
Responsible for verifying email and password credentials, ensuring the user has
verified their email address, and issuing a new refresh token upon success.
"""


class LocalLoginUseCase:
    """Handles user login with email and password."""

    def __init__(
        self,
        uow: AuthUoWPort,
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        access_token: AccessTokenPort,
        claims_provider: ClaimsProviderPort,
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
        core_settings: CoreSettings,
    ):
        self.uow = uow
        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics
        self.core_settings = core_settings

    async def execute(
        self, command: LocalLoginCommand
    ) -> tuple[UserIdentity | None, str, str]:
        async with self.uow:
            """
        Authenticate a user within a specific project context.
        Returns (profile, raw_refresh_token, access_token).
        Raises ValueError on invalid credentials or unverified email.
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

            user = await self.uow.user_query_repo.find_by_email(
                command.email, project_id=command.project_id
            )
            if not user:
                await self._logger.warning(
                    f"Login failed: Email {anonymize_email(command.email)} not found"
                )
                await self._hasher.dummy_verify()
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                self._analytics.record_event(
                    project_id=command.project_id,
                    event_type="LOGIN_FAILED",
                    user_id=None,
                    metadata=dataclasses.asdict(command.client_meta)
                    if command.client_meta
                    else None,
                )
                raise InvalidCredentialsException()

            # The admin role IS correctly persisted to the DB at registration time.
            # If the DB row was manually altered, this block restores admin privileges
            # in-memory AND persists the admin role back to the DB to keep them in sync.
            # A warning log is emitted so the self-heal is visible in the audit trail.
            if (
                self.core_settings.SUPERADMIN_EMAIL
                and command.email.strip().lower()
                == self.core_settings.SUPERADMIN_EMAIL.strip().lower()
                and command.project_id is None
                and user.role != GlobalRole.SUPERADMIN
            ):
                user.role = GlobalRole.SUPERADMIN
                await self.uow.user_command_repo.update_role(
                    user.id, GlobalRole.SUPERADMIN
                )
                await self._logger.info(
                    f"Self-healed admin role for user {user.id} - DB row role was downgraded, now corrected"
                )

            # Gatekeeper: Block users who haven't proved ownership of their email.
            if not user.is_verified:
                await self._logger.warning(
                    f"Login failed: Email {anonymize_email(command.email)} is not verified"
                )
                await (
                    self._hasher.dummy_verify()
                )  # equalise timing with "wrong password" path
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                self._analytics.record_event(
                    project_id=command.project_id,
                    tenant_id=user.id if not command.project_id else None,
                    event_type="LOGIN_FAILED",
                    user_id=user.id if command.project_id else None,
                    metadata=dataclasses.asdict(command.client_meta)
                    if command.client_meta
                    else None,
                )
                raise UnverifiedEmailException()

            stored_hash = await self.uow.user_query_repo.find_password_hash(user.id)

            # Security check: If a user registered via OAuth, they won't have a local password.
            # We must prevent them from logging in locally to avoid bypassing the OAuth provider.
            if not stored_hash:
                await self._logger.warning(
                    f"Login failed: User {user.id} has no password set (OAuth only)"
                )
                await self._hasher.dummy_verify()
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                self._analytics.record_event(
                    project_id=command.project_id,
                    tenant_id=user.id if not command.project_id else None,
                    event_type="LOGIN_FAILED",
                    user_id=user.id if command.project_id else None,
                    metadata=dataclasses.asdict(command.client_meta)
                    if command.client_meta
                    else None,
                )
                raise InvalidCredentialsException()

            # Timing attack mitigation: We only verify the hash if it exists.
            # (Note: For stricter timing attack prevention, a dummy hash comparison could be used when user is not found)
            if not await self._hasher.verify_password(command.password, stored_hash):
                await self._logger.warning(
                    f"Login failed: Invalid password for user {user.id}"
                )
                if command.is_challenged:
                    await self._rate_limiter.record_captcha_success(limit_key)
                await self._rate_limiter.record_failure(limit_key)
                self._analytics.record_event(
                    project_id=command.project_id,
                    tenant_id=user.id if not command.project_id else None,
                    event_type="LOGIN_FAILED",
                    user_id=user.id if command.project_id else None,
                    metadata=dataclasses.asdict(command.client_meta)
                    if command.client_meta
                    else None,
                )
                raise InvalidCredentialsException()

            # Restore user if soft deleted
            if getattr(user, "deleted_at", None) is not None:
                await self.uow.user_command_repo.undelete_user(user.id)
                user.deleted_at = None
                await self._email_sender.send_account_restored_email(
                    user.email.value, 
                    user.name,
                    tenant_id=user.id if not user.project_id else None,
                    project_id=command.project_id,
                )
                await self._logger.info(
                    f"User {user.id} account restored on local login"
                )

            # New Login Detection Heuristic
            # NOTE: This alert is advisory only. ip_address and user_agent are spoofable HTTP
            # headers — a sophisticated attacker can clone them to suppress this notification.
            # Treat it as a best-effort UX signal, not a security gate.
            is_first_login_post_verification = False
            if user.updated_at:
                updated_at = user.updated_at
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                delta = datetime.now(timezone.utc) - updated_at
                if delta.total_seconds() < 300:
                    is_first_login_post_verification = True

            if not is_first_login_post_verification and command.client_meta:
                active_sessions = await self.uow.refresh_token_repo.get_active_sessions(
                    user.id
                )
                is_new_device = True
                for sess in active_sessions:
                    if (
                        sess.ip_address == command.client_meta.ip_address
                        and sess.user_agent == command.client_meta.user_agent
                    ):
                        is_new_device = False
                        break

                if is_new_device:
                    import asyncio

                    device_info = await asyncio.to_thread(
                        format_device_info, command.client_meta.user_agent
                    )
                    await self._email_sender.send_login_detected_email(
                        user.email.value,
                        command.client_meta.ip_address or "Unknown IP",
                        command.client_meta.user_agent or "Unknown Device",
                        tenant_id=user.id if not user.project_id else None,
                        project_id=command.project_id,
                    )

            # Issue a long-lived refresh token. The API layer will wrap this in an HttpOnly cookie.
            family_id = uuid7()
            token = await self.uow.refresh_token_repo.create(
                user.id, family_id=family_id, client_meta=command.client_meta
            )

            # Generate the short-lived access token
            custom_claims = await self._claims_provider.get_custom_claims(
                self.uow, user.id
            )
            combined_claims: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                combined_claims.update(custom_claims)
            private_key_override = (
                await self.uow.project_key_repo.get_private_key(command.project_id)
                if command.project_id
                else None
            )
            access_token = self._access_token.create(
                user,
                extra_claims=combined_claims,
                private_key_override=private_key_override,
            )

            await self._logger.info(
                f"User {user.id} logged in successfully via local auth"
            )

            if command.is_challenged:
                await self._rate_limiter.record_success(limit_key)

            self._analytics.record_event(
                project_id=command.project_id,
                tenant_id=user.id if not command.project_id else None,
                event_type="LOGIN_SUCCESS",
                user_id=user.id if command.project_id else None,
                metadata=dataclasses.asdict(command.client_meta)
                if command.client_meta
                else None,
            )

            profile = await self.uow.user_query_repo.find_by_id(user.id)

            return profile, token, access_token
