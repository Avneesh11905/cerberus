from uuid6 import uuid7

from src.core.config import get_settings
from src.modules.authentication.application.commands import (
    TenantOAuthCallbackCommand,
)
from src.modules.authentication.application.ports import (
    AccessTokenPort,
    ClaimsProviderPort,
    EmailSenderPort,
)
from src.modules.authentication.application.ports.security.oauth_service import (
    OAuthServicePort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.application.utils import format_device_info
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authorization.domain.enums import GlobalRole
from src.shared.domain.entities import ClientMetadata

"""
Use Case: TenantOAuthCallbackUseCase

Handles the OAuth callback for Cerberus Dashboard users (tenants).
- Account Linking: Matches exactly by OAuth provider subject ID, or links to an existing account with the same email.
- Fallback: Creates a new user if no match is found.
  - Assigns UserRole.SUPERADMIN if email matches SUPERADMIN_EMAIL, else UserRole.TENANT
"""


class TenantOAuthCallbackUseCase[SessionType, RequestType]:
    """
    Orchestrates the OAuth callback flow for Cerberus Dashboard tenants.

    Tenants log into the global Cerberus platform — no project scoping.
    Role is SUPERADMIN if the email matches the configured superadmin,
    otherwise TENANT.
    """

    def __init__(
        self,
        uow: AuthUoWPort,
        email_sender: EmailSenderPort,
        access_token: AccessTokenPort,
        claims_provider: ClaimsProviderPort,
        oauth_service: OAuthServicePort[RequestType],
    ):
        self.uow = uow
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._oauth_service = oauth_service

    async def _check_new_login(
        self,
        uow: AuthUoWPort,
        user: UserIdentity,
        client_meta: ClientMetadata | None,
    ) -> None:
        if not client_meta:
            return
        active_sessions = await uow.refresh_token_repo.get_active_sessions(user.id)
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
                to_email=user.email.value,
                ip_address=client_meta.ip_address or "Unknown IP",
                device_info=device_info,
                tenant_id=user.id,
            )

    def _resolve_role(self, email: str) -> GlobalRole:
        super_email = get_settings().core.SUPERADMIN_EMAIL
        if super_email and email.strip().lower() == super_email.strip().lower():
            return GlobalRole.SUPERADMIN
        return GlobalRole.TENANT

    async def execute(
        self, command: TenantOAuthCallbackCommand
    ) -> tuple[UserIdentity, str, str, bool]:
        async with self.uow:
            """
            Process a tenant OAuth callback.

            Returns:
                (user_identity, raw_refresh_token, access_token, is_new_user)
            """
            user_info = await self._oauth_service.exchange_code_for_user_info(
                command.provider, None, command.request, uow=self.uow
            )
            oauth_sub = user_info.sub
            email = user_info.email.value
            name = user_info.name
            picture = user_info.picture
            role = self._resolve_role(email)

            # Step 1: Exact provider+sub match
            user = await self.uow.user_query_repo.find_by_oauth(
                command.provider, oauth_sub, project_id=None
            )
            if user:
                if getattr(user, "deleted_at", None) is not None:
                    await self.uow.user_command_repo.undelete_user(user.id)
                    user.deleted_at = None
                    await self._email_sender.send_account_restored_email(
                        user.email.value,
                        user.name,
                        tenant_id=user.id,
                    )

                from src.modules.authorization.domain.enums import GlobalRole

                if role == GlobalRole.SUPERADMIN and user.role != GlobalRole.SUPERADMIN:
                    user.role = GlobalRole.SUPERADMIN

                await self._check_new_login(self.uow, user, command.client_meta)

                # Update the name, picture, and verified status based on the OAuth provider's payload
                await self.uow.user_command_repo.update_oauth_profile(
                    user.id, name=name, picture=str(picture) if picture else None
                )

                family_id = uuid7()
                refresh_token = await self.uow.refresh_token_repo.create(
                    user.id,
                    family_id=family_id,
                    auth_provider=command.provider,
                    client_meta=command.client_meta,
                )
                custom_claims = await self._claims_provider.get_custom_claims(
                    self.uow, user.id
                )
                extra_claims: dict[str, object] = {"family_id": str(family_id)}
                if custom_claims:
                    extra_claims.update(custom_claims)
                access_token = self._access_token.create(
                    user, extra_claims=extra_claims
                )
                return user, refresh_token, access_token, False

            # Step 2: Email match → account linking
            user = await self.uow.user_query_repo.find_by_email(email, project_id=None)
            if user:
                if getattr(user, "deleted_at", None) is not None:
                    await self.uow.user_command_repo.undelete_user(user.id)
                    user.deleted_at = None
                    await self._email_sender.send_account_restored_email(
                        user.email.value,
                        user.name,
                        tenant_id=user.id,
                    )

                from src.modules.authorization.domain.enums import GlobalRole

                if role == GlobalRole.SUPERADMIN and user.role != GlobalRole.SUPERADMIN:
                    user.role = GlobalRole.SUPERADMIN
                    await self.uow.user_command_repo.update_role(
                        user.id, GlobalRole.SUPERADMIN
                    )

                await self.uow.user_command_repo.link_oauth_account(
                    user.id, command.provider, oauth_sub, project_id=None
                )
                await self._check_new_login(self.uow, user, command.client_meta)

                # Update the name, picture, and verified status based on the OAuth provider's payload
                await self.uow.user_command_repo.update_oauth_profile(
                    user.id, name=name, picture=str(picture) if picture else None
                )

                family_id = uuid7()
                refresh_token = await self.uow.refresh_token_repo.create(
                    user.id,
                    family_id=family_id,
                    auth_provider=command.provider,
                    client_meta=command.client_meta,
                )
                custom_claims = await self._claims_provider.get_custom_claims(
                    self.uow, user.id
                )
                extra_claims = {"family_id": str(family_id)}
                if custom_claims:
                    extra_claims.update(custom_claims)
                access_token = self._access_token.create(
                    user, extra_claims=extra_claims
                )
                return user, refresh_token, access_token, False

            # Step 3: Create new tenant user
            new_user = await self.uow.user_command_repo.create_user_with_oauth(
                email=email,
                name=name,
                picture=str(picture) if picture else None,
                provider=command.provider,
                oauth_sub=oauth_sub,
                project_id=None,
                role=role,
            )
            family_id = uuid7()
            refresh_token = await self.uow.refresh_token_repo.create(
                new_user.id,
                family_id=family_id,
                auth_provider=command.provider,
                client_meta=command.client_meta,
            )
            custom_claims = await self._claims_provider.get_custom_claims(
                self.uow, new_user.id
            )
            extra_claims = {"family_id": str(family_id)}
            if custom_claims:
                extra_claims.update(custom_claims)
            access_token = self._access_token.create(
                new_user, extra_claims=extra_claims
            )
            await self._email_sender.send_welcome_email(
                new_user.email.value,
                new_user.name,
                tenant_id=new_user.id,
            )
            return new_user, refresh_token, access_token, True
