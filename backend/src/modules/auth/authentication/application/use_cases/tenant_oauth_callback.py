"""
Use Case: TenantOAuthCallbackUseCase

Handles the OAuth callback for Cerberus Dashboard users (tenants).
Unlike ProjectUserOAuthCallbackUseCase, this use case:
  - Never takes a project_id (tenants are global, not scoped to a project)
  - Does not need ProjectKeyRepositoryPort
  - Assigns UserRole.SUPERADMIN if email matches SUPERADMIN_EMAIL, else UserRole.TENANT
"""

from uuid6 import uuid7

from src.core.config import core_settings
from src.modules.auth.authentication.application.ports import (
    RefreshTokenRepositoryPort,
    UserQueryRepositoryPort,
    UserCommandRepositoryPort,
    EmailSenderPort,
    AccessTokenPort,
    ClaimsProviderPort,
)
from src.modules.auth.authentication.application.utils import format_device_info
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.shared.domain.entities import ClientMetadata
from src.shared.application.ports import UoWPort
from src.modules.auth.authorization.domain.enums import GlobalRole

from src.modules.auth.authentication.application.ports.security.oauth_service import (
    OAuthServicePort,
)


class TenantOAuthCallbackUseCase[SessionType, RequestType]:
    """
    Orchestrates the OAuth callback flow for Cerberus Dashboard tenants.

    Tenants log into the global Cerberus platform — no project scoping.
    Role is SUPERADMIN if the email matches the configured superadmin,
    otherwise TENANT.
    """

    def __init__(
        self,
        user_query_repo: "UserQueryRepositoryPort",
        user_command_repo: "UserCommandRepositoryPort",
        refresh_repo: "RefreshTokenRepositoryPort",
        email_sender: "EmailSenderPort",
        access_token: "AccessTokenPort",
        claims_provider: "ClaimsProviderPort",
        oauth_service: OAuthServicePort[SessionType, RequestType],
    ):
        self._user_query_repo = user_query_repo
        self._user_command_repo = user_command_repo
        self._refresh_repo = refresh_repo
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._oauth_service = oauth_service

    async def _check_new_login(
        self,
        session: SessionType,
        user: UserIdentity,
        client_meta: ClientMetadata | None,
    ) -> None:
        if not client_meta:
            return
        active_sessions = await self._refresh_repo.get_active_sessions(session, user.id)
        is_new_device = all(
            sess.ip_address != client_meta.ip_address
            or sess.user_agent != client_meta.user_agent
            for sess in active_sessions
        )
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

    def _resolve_role(self, email: str) -> GlobalRole:
        if (
            core_settings.SUPERADMIN_EMAIL
            and email.strip().lower() == core_settings.SUPERADMIN_EMAIL.strip().lower()
        ):
            return GlobalRole.SUPERADMIN
        return GlobalRole.TENANT

    async def execute(
        self,
        uow: UoWPort[SessionType],
        provider: str,
        request: RequestType,
        client_meta: ClientMetadata | None = None,
    ) -> tuple[UserIdentity, str, str, bool]:
        """
        Process a tenant OAuth callback.

        Returns:
            (user_identity, raw_refresh_token, access_token, is_new_user)
        """
        user_info = await self._oauth_service.exchange_code_for_user_info(
            provider, None, request, uow.session
        )
        provider = user_info.provider
        oauth_sub = user_info.sub
        email = user_info.email
        name = user_info.name
        picture = user_info.picture
        role = self._resolve_role(email)

        # Step 1: Exact provider+sub match
        user = await self._user_query_repo.find_by_oauth(
            uow.session, provider, oauth_sub, project_id=None
        )
        if user:
            if getattr(user, "deleted_at", None) is not None:
                await self._user_command_repo.undelete_user(uow.session, user.id)
                user.deleted_at = None
                await self._email_sender.send_account_restored_email(
                    user.email, user.name
                )

            from src.modules.auth.authorization.domain.enums import GlobalRole

            if role == GlobalRole.SUPERADMIN and user.role != GlobalRole.SUPERADMIN:
                user.role = GlobalRole.SUPERADMIN

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
            extra_claims: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                extra_claims.update(custom_claims)
            access_token = self._access_token.create(user, extra_claims=extra_claims)
            return user, refresh_token, access_token, False

        # Step 2: Email match → account linking
        user = await self._user_query_repo.find_by_email(
            uow.session, email, project_id=None
        )
        if user:
            if getattr(user, "deleted_at", None) is not None:
                await self._user_command_repo.undelete_user(uow.session, user.id)
                user.deleted_at = None
                await self._email_sender.send_account_restored_email(
                    user.email, user.name
                )

            from src.modules.auth.authorization.domain.enums import GlobalRole

            if role == GlobalRole.SUPERADMIN and user.role != GlobalRole.SUPERADMIN:
                user.role = GlobalRole.SUPERADMIN
                await self._user_command_repo.update_role(
                    uow.session, user.id, GlobalRole.SUPERADMIN
                )

            await self._user_command_repo.link_oauth_account(
                uow.session, user.id, provider, oauth_sub, project_id=None
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
            extra_claims = {"family_id": str(family_id)}
            if custom_claims:
                extra_claims.update(custom_claims)
            access_token = self._access_token.create(user, extra_claims=extra_claims)
            return user, refresh_token, access_token, False

        # Step 3: Create new tenant user
        new_user = await self._user_command_repo.create_user_with_oauth(
            session=uow.session,
            email=email,
            name=name,
            picture=str(picture) if picture else None,
            provider=provider,
            oauth_sub=oauth_sub,
            project_id=None,
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
        extra_claims = {"family_id": str(family_id)}
        if custom_claims:
            extra_claims.update(custom_claims)
        access_token = self._access_token.create(new_user, extra_claims=extra_claims)
        await self._email_sender.send_welcome_email(new_user.email, new_user.name)
        return new_user, refresh_token, access_token, True
