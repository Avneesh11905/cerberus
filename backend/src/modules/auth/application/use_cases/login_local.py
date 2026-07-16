"""
Orchestrates the local authentication flow.
Responsible for verifying email and password credentials, ensuring the user has
verified their email address, and issuing a new refresh token upon success.
"""

from datetime import datetime, timezone
from uuid import UUID

from uuid6 import uuid7

from src.core.config import core_settings
from src.core.exceptions import TurnstileVerificationFailed
from src.modules.auth.application.ports import (
    PasswordHasherPort,
    RefreshTokenRepositoryPort,
    UserRepositoryPort,
)
from src.modules.auth.application.ports.email_sender import EmailSenderPort
from src.modules.auth.application.ports.repository.project import ProjectRepositoryPort
from src.modules.auth.application.ports.security.access_token import AccessTokenPort
from src.modules.auth.application.ports.security.claims_provider import (
    ClaimsProviderPort,
)
from src.modules.auth.application.utils import anonymize_email, format_device_info
from src.modules.auth.domain import UserIdentity
from src.modules.auth.domain.exceptions import (
    InvalidCredentialsException,
    UnverifiedEmailException,
)
from src.modules.auth.domain.session import ClientMetadata
from src.shared.application.ports.analytics import AnalyticsEventPort
from src.shared.application.ports.logger import LoggerPort
from src.shared.application.ports.rate_limiter import RateLimiterPort
from src.shared.application.ports.turnstile import TurnstilePort
from src.shared.application.ports.uow import UoWPort
from src.shared.domain.enums import UserRole


class LoginLocalUserUseCase[SessionType]:
    """Handles user login with email and password."""

    def __init__(
        self,
        user_repo: UserRepositoryPort[SessionType],
        refresh_repo: RefreshTokenRepositoryPort[SessionType],
        hasher: PasswordHasherPort,
        logger: LoggerPort,
        email_sender: EmailSenderPort,
        access_token: AccessTokenPort,
        claims_provider: ClaimsProviderPort,
        project_repo: ProjectRepositoryPort[SessionType],
        rate_limiter: RateLimiterPort,
        turnstile: TurnstilePort,
        analytics: AnalyticsEventPort,
    ):
        self._user_repo = user_repo
        self._refresh_repo = refresh_repo
        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._project_repo = project_repo
        self._rate_limiter = rate_limiter
        self._turnstile = turnstile
        self._analytics = analytics

    async def execute(
        self,
        uow: UoWPort[SessionType],
        email: str,
        password: str,
        client_meta: ClientMetadata | None = None,
        project_id: UUID | None = None,
        is_challenged: bool = False,
        turnstile_token: str | None = None,
    ) -> tuple[UserIdentity, str, str]:
        """
        Authenticate a user within a specific project context.
        Returns (user, raw_refresh_token, access_token).
        Raises ValueError on invalid credentials or unverified email.
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

        user = await self._user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if not user:
            await self._logger.warning(
                f"Login failed: Email {anonymize_email(email)} not found"
            )
            await self._hasher.dummy_verify()
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            self._analytics.record_event(
                project_id=project_id,
                event_type="LOGIN_FAILED",
                user_id=None,
                metadata=client_meta.model_dump() if client_meta else None,
            )
            raise InvalidCredentialsException()

        # The admin role IS correctly persisted to the DB at registration time.
        # If the DB row was manually altered, this block restores admin privileges
        # in-memory AND persists the admin role back to the DB to keep them in sync.
        # A warning log is emitted so the self-heal is visible in the audit trail.
        if (
            core_settings.SUPERADMIN_EMAIL
            and email.strip().lower() == core_settings.SUPERADMIN_EMAIL.strip().lower()
            and project_id is None
            and user.role != UserRole.SUPERADMIN
        ):
            user.role = UserRole.SUPERADMIN
            await self._user_repo.update_role(uow.session, user.id, UserRole.SUPERADMIN)
            await self._logger.info(
                f"Self-healed admin role for user {user.id} - DB row role was downgraded, now corrected"
            )

        # Gatekeeper: Block users who haven't proved ownership of their email.
        if not user.is_verified:
            await self._logger.warning(
                f"Login failed: Email {anonymize_email(email)} is not verified"
            )
            await (
                self._hasher.dummy_verify()
            )  # equalise timing with "wrong password" path
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            self._analytics.record_event(
                project_id=project_id,
                tenant_id=user.id if not project_id else None,
                event_type="LOGIN_FAILED",
                user_id=user.id if project_id else None,
                metadata=client_meta.model_dump() if client_meta else None,
            )
            raise UnverifiedEmailException()

        stored_hash = await self._user_repo.find_password_hash(uow.session, user.id)

        # Security check: If a user registered via OAuth, they won't have a local password.
        # We must prevent them from logging in locally to avoid bypassing the OAuth provider.
        if not stored_hash:
            await self._logger.warning(
                f"Login failed: User {user.id} has no password set (OAuth only)"
            )
            await self._hasher.dummy_verify()
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            self._analytics.record_event(
                project_id=project_id,
                tenant_id=user.id if not project_id else None,
                event_type="LOGIN_FAILED",
                user_id=user.id if project_id else None,
                metadata=client_meta.model_dump() if client_meta else None,
            )
            raise InvalidCredentialsException()

        # Timing attack mitigation: We only verify the hash if it exists.
        # (Note: For stricter timing attack prevention, a dummy hash comparison could be used when user is not found)
        if not await self._hasher.verify_password(password, stored_hash):
            await self._logger.warning(
                f"Login failed: Invalid password for user {user.id}"
            )
            if is_challenged:
                await self._rate_limiter.record_captcha_success(limit_key)
            await self._rate_limiter.record_failure(limit_key)
            self._analytics.record_event(
                project_id=project_id,
                tenant_id=user.id if not project_id else None,
                event_type="LOGIN_FAILED",
                user_id=user.id if project_id else None,
                metadata=client_meta.model_dump() if client_meta else None,
            )
            raise InvalidCredentialsException()

        # Restore user if soft deleted
        if getattr(user, "deleted_at", None) is not None:
            await self._user_repo.undelete_user(uow.session, user.id)
            user.deleted_at = None
            await self._email_sender.send_account_restored_email(user.email, user.name)
            await self._logger.info(f"User {user.id} account restored on local login")

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

        if not is_first_login_post_verification and client_meta:
            active_sessions = await self._refresh_repo.get_active_sessions(
                uow.session, user.id
            )
            is_new_device = True
            for sess in active_sessions:
                if (
                    sess.ip_address == client_meta.ip_address
                    and sess.user_agent == client_meta.user_agent
                ):
                    is_new_device = False
                    break

            if is_new_device:
                import asyncio

                device_info = await asyncio.to_thread(
                    format_device_info, client_meta.user_agent
                )
                await self._email_sender.send_login_detected_email(
                    to_email=user.email,
                    ip_address=client_meta.ip_address or "Unknown IP",
                    device_info=device_info,
                )

        # Issue a long-lived refresh token. The API layer will wrap this in an HttpOnly cookie.
        family_id = uuid7()
        token = await self._refresh_repo.create(
            uow.session, user.id, family_id=family_id, client_meta=client_meta
        )

        # Generate the short-lived access token
        custom_claims = await self._claims_provider.get_custom_claims(
            uow.session, user.id
        )
        combined_claims: dict[str, object] = {"family_id": str(family_id)}
        if custom_claims:
            combined_claims.update(custom_claims)
        private_key_override = (
            await self._project_repo.get_private_key(uow.session, project_id)
            if project_id
            else None
        )
        access_token = self._access_token.create(
            user,
            extra_claims=combined_claims,
            private_key_override=private_key_override,
        )

        await self._logger.info(f"User {user.id} logged in successfully via local auth")

        if is_challenged:
            await self._rate_limiter.record_success(limit_key)

        self._analytics.record_event(
            project_id=project_id,
            tenant_id=user.id if not project_id else None,
            event_type="LOGIN_SUCCESS",
            user_id=user.id if project_id else None,
            metadata=client_meta.model_dump() if client_meta else None,
        )

        return user, token, access_token
