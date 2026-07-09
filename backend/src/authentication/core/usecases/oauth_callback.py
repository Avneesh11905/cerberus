"""
Handles the core business logic for processing OAuth provider callbacks.
It implements an "Account Linking" strategy:
1. Exact match: If the provider's subject ID matches an existing linked account, log them in.
2. Email match: If the email matches an existing local/OAuth user, link this new provider to their account to avoid duplicate accounts.
3. Fallback: Create a brand new user.
"""

from uuid import UUID

from uuid6 import uuid7

from src.authentication.core.domain import UserIdentity, UserRole
from src.authentication.core.domain.session import ClientMetadata
from src.authentication.core.domain.user import OAuthUserInfo
from src.authentication.core.ports import RefreshTokenRepositoryPort, UserRepositoryPort
from src.authentication.core.ports.email_sender import EmailSenderPort
from src.authentication.core.ports.repository.project import ProjectRepositoryPort
from src.authentication.core.ports.security.access_token import AccessTokenPort
from src.authentication.core.ports.security.claims_provider import ClaimsProviderPort
from src.authentication.core.utils import format_device_info
from src.shared.config import app_settings
from src.shared.core.ports.uow import UoWPort


class OAuthCallbackUseCase[SessionType]:
    """
    Orchestrates the OAuth callback flow:
    1. Upsert user with account-linking (find by provider, email, or create new).
    2. Issue a refresh token for the session.

    Routes call this use case and handle HTTP response/cookie construction themselves.
    """

    def __init__(
        self,
        user_repo: "UserRepositoryPort",
        refresh_repo: "RefreshTokenRepositoryPort",
        email_sender: "EmailSenderPort",
        access_token: "AccessTokenPort",
        claims_provider: "ClaimsProviderPort",
        project_repo: "ProjectRepositoryPort",
    ):
        self._user_repo = user_repo
        self._refresh_repo = refresh_repo
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._project_repo = project_repo

    async def _check_new_login(
        self,
        session: SessionType,
        user: UserIdentity,
        client_meta: ClientMetadata | None,
    ) -> None:
        """
        Send a login-from-new-device alert email if the IP+UA combination isn't
        recognised from an existing active session.

        NOTE: This is an advisory security alert only. Both ip_address and user_agent
        are trivially spoofable HTTP headers — an attacker who clones these values from
        a leaked session can suppress this notification. Do not rely on it as a security
        gate; treat it as a best-effort user-facing UX signal only.
        """
        if not client_meta:
            return
        active_sessions = await self._refresh_repo.get_active_sessions(session, user.id)
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
            device_info = await asyncio.to_thread(format_device_info, client_meta.user_agent)
            await self._email_sender.send_login_detected_email(
                to_email=user.email,
                ip_address=client_meta.ip_address or "Unknown IP",
                device_info=device_info,
            )

    async def execute(
        self,
        uow: UoWPort[SessionType],
        user_info: OAuthUserInfo,
        client_meta: ClientMetadata | None = None,
        project_id: UUID | None = None,
        role: UserRole = UserRole.USER,
    ) -> tuple[UserIdentity, str, str, bool]:
        """
        Process an OAuth callback.

        Args:
            session: Database session (injected by FastAPI dependency).
            user_info: Structured OAuth data payload from the provider.

        Returns:
            (user_identity, raw_refresh_token, is_new_user)
        """
        provider = user_info.provider
        oauth_sub = user_info.sub
        email = user_info.email
        name = user_info.name
        picture = user_info.picture

        if (
            app_settings.ADMIN_EMAIL
            and email.strip().lower() == app_settings.ADMIN_EMAIL.strip().lower()
            and project_id is None
        ):
            role = UserRole.ADMIN

        # Step 1: Check if this exact provider+sub already exists
        user = await self._user_repo.find_by_oauth(
            uow.session, provider, oauth_sub, project_id=project_id
        )
        if user:
            if getattr(user, "deleted_at", None) is not None:
                await self._user_repo.undelete_user(uow.session, user.id)
                user.deleted_at = None
                await self._email_sender.send_account_restored_email(
                    user.email, user.name
                )

            if role == UserRole.ADMIN and user.role != UserRole.ADMIN:
                user.role = UserRole.ADMIN

            await self._check_new_login(uow.session, user, client_meta)

            # We explicitly DO NOT update the name/picture here so we don't overwrite user preferences
            family_id = uuid7()
            refresh_token = await self._refresh_repo.create(
                uow.session,
                user.id,
                family_id=family_id,
                auth_provider=provider,
                client_meta=client_meta,
            )

            custom_claims = await self._claims_provider.get_custom_claims(
                uow.session, user.id
            )
            combined_claims: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                combined_claims.update(custom_claims)
            access_token = self._access_token.create(user, extra_claims=combined_claims)

            return user, refresh_token, access_token, False
        # Step 2: Check if a user with this email already exists (account linking)
        user = await self._user_repo.find_by_email(
            uow.session, email, project_id=project_id
        )
        if user:
            if getattr(user, "deleted_at", None) is not None:
                await self._user_repo.undelete_user(uow.session, user.id)
                user.deleted_at = None
                await self._email_sender.send_account_restored_email(
                    user.email, user.name
                )

            if role == UserRole.ADMIN and user.role != UserRole.ADMIN:
                user.role = UserRole.ADMIN

            await self._user_repo.link_oauth_account(
                uow.session, user.id, provider, oauth_sub, project_id=project_id
            )

            await self._check_new_login(uow.session, user, client_meta)

            family_id = uuid7()
            refresh_token = await self._refresh_repo.create(
                uow.session,
                user.id,
                family_id=family_id,
                auth_provider=provider,
                client_meta=client_meta,
            )

            custom_claims = await self._claims_provider.get_custom_claims(
                uow.session, user.id
            )
            combined_claims_email: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                combined_claims_email.update(custom_claims)
            access_token = self._access_token.create(
                user, extra_claims=combined_claims_email
            )

            return user, refresh_token, access_token, False
        # Step 3: Create brand new user
        new_user = await self._user_repo.create_user_with_oauth(
            session=uow.session,
            email=email,
            name=name,
            picture=str(picture) if picture else None,
            provider=provider,
            oauth_sub=oauth_sub,
            project_id=project_id,
            role=role,
        )
        family_id = uuid7()
        refresh_token = await self._refresh_repo.create(
            uow.session,
            new_user.id,
            family_id=family_id,
            auth_provider=provider,
            client_meta=client_meta,
        )

        custom_claims = await self._claims_provider.get_custom_claims(
            uow.session, new_user.id
        )
        combined_claims_new: dict[str, object] = {"family_id": str(family_id)}
        if custom_claims:
            combined_claims_new.update(custom_claims)
        private_key_override = (
            await self._project_repo.get_private_key(uow.session, project_id)
            if project_id
            else None
        )
        access_token = self._access_token.create(
            new_user,
            extra_claims=combined_claims_new,
            private_key_override=private_key_override,
        )

        await self._email_sender.send_welcome_email(new_user.email, new_user.name)

        return new_user, refresh_token, access_token, True
