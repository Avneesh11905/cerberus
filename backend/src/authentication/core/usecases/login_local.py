"""
Orchestrates the local authentication flow.
Responsible for verifying email and password credentials, ensuring the user has 
verified their email address, and issuing a new refresh token upon success.
"""

from datetime import datetime, timezone
from uuid6 import uuid7
from src.shared.config import app_settings
from src.authentication.core.domain import UserIdentity, UserRole
from src.authentication.core.domain.exceptions import (
    InvalidCredentialsException,
    UnverifiedEmailException,
)
from src.authentication.core.domain.session import ClientMetadata
from src.authentication.core.ports import (
    PasswordHasherPort,
    RefreshTokenRepositoryPort,
    UserRepositoryPort,
)
from src.authentication.core.ports.email_sender import EmailSenderPort
from src.authentication.core.ports.repository.project import ProjectRepositoryPort
from src.authentication.core.ports.security.access_token import AccessTokenPort
from src.authentication.core.ports.security.claims_provider import ClaimsProviderPort
from src.shared.core.ports.logger import LoggerPort
from src.shared.core.ports.uow import UoWPort
from src.authentication.core.utils import anonymize_email
from uuid import UUID


class LoginLocalUserUseCase[SessionType]:
    """Handles user login with email and password."""

    def __init__(self, user_repo: UserRepositoryPort[SessionType], refresh_repo: RefreshTokenRepositoryPort[SessionType], hasher: PasswordHasherPort, logger: LoggerPort, email_sender: EmailSenderPort, access_token: AccessTokenPort, claims_provider: ClaimsProviderPort, project_repo: ProjectRepositoryPort[SessionType]):
        self._user_repo = user_repo
        self._refresh_repo = refresh_repo
        self._hasher = hasher
        self._logger = logger
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._project_repo = project_repo

    async def execute(self, uow: UoWPort[SessionType], email: str, password: str, client_meta: ClientMetadata | None = None, project_id: UUID | None = None) -> tuple[UserIdentity, str, str]:
        """
        Authenticate a user within a specific project context. 
        Returns (user, raw_refresh_token, access_token).
        Raises ValueError on invalid credentials or unverified email.
        """
        user = await self._user_repo.find_by_email(uow.session, email, project_id=project_id)
        if not user:
            await self._logger.warning(f"Login failed: Email {anonymize_email(email)} not found")
            await self._hasher.dummy_verify()
            raise InvalidCredentialsException()
            
        # Note: This is a recovery/self-healing mechanism.
        # The admin role IS correctly persisted to the DB at registration time.
        # This in-memory mutation ensures the JWT reflects admin privileges 
        # even if the DB row was manually altered, acting as a fallback safety-net.
        if app_settings.ADMIN_EMAIL and email.strip().lower() == app_settings.ADMIN_EMAIL.strip().lower() and project_id is None and user.role != UserRole.ADMIN:
            user.role = UserRole.ADMIN

        # Gatekeeper: Block users who haven't proved ownership of their email.
        if not user.is_verified:
            await self._logger.warning(f"Login failed: Email {anonymize_email(email)} is not verified")
            await self._hasher.dummy_verify()   # equalise timing with "wrong password" path
            raise UnverifiedEmailException()

        stored_hash = await self._user_repo.find_password_hash(uow.session, user.id)
        
        # Security check: If a user registered via OAuth, they won't have a local password.
        # We must prevent them from logging in locally to avoid bypassing the OAuth provider.
        if not stored_hash:
            await self._logger.warning(f"Login failed: User {user.id} has no password set (OAuth only)")
            await self._hasher.dummy_verify()
            raise InvalidCredentialsException()

        # Timing attack mitigation: We only verify the hash if it exists. 
        # (Note: For stricter timing attack prevention, a dummy hash comparison could be used when user is not found)
        if not await self._hasher.verify_password(password, stored_hash):
            await self._logger.warning(f"Login failed: Invalid password for user {user.id}")
            raise InvalidCredentialsException()

        # Restore user if soft deleted
        if getattr(user, 'deleted_at', None) is not None:
            await self._user_repo.undelete_user(uow.session, user.id)
            user.deleted_at = None
            await self._email_sender.send_account_restored_email(user.email, user.name)
            await self._logger.info(f"User {user.id} account restored on local login")

        # New Login Detection Heuristic
        is_first_login_post_verification = False
        if user.updated_at:
            updated_at = user.updated_at
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - updated_at
            if delta.total_seconds() < 300:
                is_first_login_post_verification = True

        if not is_first_login_post_verification and client_meta:
            active_sessions = await self._refresh_repo.get_active_sessions(uow.session, user.id)
            is_new_device = True
            for sess in active_sessions:
                if sess.ip_address == client_meta.ip_address and sess.user_agent == client_meta.user_agent:
                    is_new_device = False
                    break
            
            if is_new_device:
                await self._email_sender.send_login_detected_email(
                    to_email=user.email,
                    ip_address=client_meta.ip_address or "Unknown IP",
                    device_info=client_meta.user_agent or "Unknown Device"
                )

        # Issue a long-lived refresh token. The API layer will wrap this in an HttpOnly cookie.
        family_id = uuid7()
        token = await self._refresh_repo.create(uow.session, user.id, family_id=family_id, client_meta=client_meta)
        
        # Generate the short-lived access token
        custom_claims = await self._claims_provider.get_custom_claims(uow.session, user.id)
        combined_claims: dict[str, object] = {"family_id": str(family_id)}
        if custom_claims:
            combined_claims.update(custom_claims)
        private_key_override = await self._project_repo.get_private_key(uow.session, project_id) if project_id else None
        access_token = self._access_token.create(user, extra_claims=combined_claims, private_key_override=private_key_override)
        
        await self._logger.info(f"User {user.id} logged in successfully via local auth")
        return user, token, access_token
