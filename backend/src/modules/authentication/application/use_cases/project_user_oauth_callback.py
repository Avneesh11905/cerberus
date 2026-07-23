from typing import Any

from uuid6 import uuid7

from src.modules.authentication.application.commands import (
    ProjectUserOAuthCallbackCommand,
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
from src.modules.authorization.application.services.role_provisioning import (
    RoleProvisioningService,
)
from src.shared.domain.entities import ClientMetadata
from src.shared.domain.value_objects import HttpsUrl

"""
Handles the core business logic for processing OAuth provider callbacks for end-users.
It implements an "Account Linking" strategy:
1. Exact match: If the provider's subject ID matches an existing linked account, log them in.
2. Email match: If the email matches an existing local/OAuth user, link this new provider to their account to avoid duplicate accounts.
3. Fallback: Create a brand new user.

Note: For Cerberus Dashboard (tenant) callbacks, see tenant_oauth_callback.py.
"""


class ProjectUserOAuthCallbackUseCase[SessionType, RequestType]:
    """
    Orchestrates the OAuth callback flow:
    1. Exchanges auth code for user info via OAuthServicePort.
    2. Upsert user with account-linking (find by provider, email, or create new).
    3. Issue a refresh token for the session.

    Routes call this use case and handle HTTP response/cookie construction themselves.
    """

    def __init__(
        self,
        uow: AuthUoWPort,
        email_sender: EmailSenderPort,
        access_token: AccessTokenPort,
        claims_provider: ClaimsProviderPort,
        oauth_service: OAuthServicePort[Any],
        role_provisioning: RoleProvisioningService,
    ):
        self.uow = uow
        self._email_sender = email_sender
        self._access_token = access_token
        self._claims_provider = claims_provider
        self._oauth_service = oauth_service
        self._role_provisioning = role_provisioning

    async def _check_new_login(
        self,
        uow: AuthUoWPort,
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
        active_sessions = await uow.refresh_token_repo.get_active_sessions(user.id)
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
                to_email=user.email.value,
                ip_address=client_meta.ip_address or "Unknown IP",
                device_info=device_info,
                tenant_id=None,
                project_id=user.project_id,
            )

    async def execute(
        self, command: ProjectUserOAuthCallbackCommand
    ) -> tuple[UserIdentity, str, str, bool, HttpsUrl | None]:
        async with self.uow:
            """
            Process a project user OAuth callback.

            Returns:
                (user_identity, raw_refresh_token, access_token, is_new_user, fallback_frontend_url)
            """
            project = await self.uow.project_query_repo.get_by_id(command.project_id)
            fallback_frontend_url = project.frontend_url if project else None

            user_info = await self._oauth_service.exchange_code_for_user_info(
                command.provider, command.project_id, command.request, uow=self.uow
            )
            oauth_sub = user_info.sub
            email = user_info.email.value
            name = user_info.name
            picture = user_info.picture

            role = await self._role_provisioning.determine_default_role(
                email, command.project_id
            )

            # Step 1: Check if this exact provider+sub already exists
            user = await self.uow.user_query_repo.find_by_oauth(
                command.provider, oauth_sub, project_id=command.project_id
            )
            if user:
                if getattr(user, "deleted_at", None) is not None:
                    await self.uow.user_command_repo.undelete_user(user.id)
                    user.deleted_at = None
                    await self._email_sender.send_account_restored_email(
                        user.email.value, 
                        user.name,
                        tenant_id=None,
                        project_id=command.project_id,
                    )

                await self._check_new_login(self.uow, user, command.client_meta)

                # We explicitly DO NOT update the name/picture here so we don't overwrite user preferences
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
                combined_claims: dict[str, object] = {"family_id": str(family_id)}
                if custom_claims:
                    combined_claims.update(custom_claims)
                access_token = self._access_token.create(
                    user, extra_claims=combined_claims
                )

                return user, refresh_token, access_token, False, fallback_frontend_url
            # Step 2: Check if a user with this email already exists (account linking)
            user = await self.uow.user_query_repo.find_by_email(
                email, project_id=command.project_id
            )
            if user:
                if getattr(user, "deleted_at", None) is not None:
                    await self.uow.user_command_repo.undelete_user(user.id)
                    user.deleted_at = None
                    await self._email_sender.send_account_restored_email(
                        user.email.value, 
                        user.name,
                        tenant_id=None,
                        project_id=command.project_id,
                    )

                await self.uow.user_command_repo.link_oauth_account(
                    user.id, command.provider, oauth_sub, project_id=command.project_id
                )

                await self._check_new_login(self.uow, user, command.client_meta)

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
                combined_claims_email: dict[str, object] = {"family_id": str(family_id)}
                if custom_claims:
                    combined_claims_email.update(custom_claims)
                access_token = self._access_token.create(
                    user, extra_claims=combined_claims_email
                )

                return user, refresh_token, access_token, False, fallback_frontend_url
            # Step 3: Create brand new user
            new_user = await self.uow.user_command_repo.create_user_with_oauth(
                email=email,
                name=name,
                picture=str(picture) if picture else None,
                provider=command.provider,
                oauth_sub=oauth_sub,
                project_id=command.project_id,
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
            combined_claims_new: dict[str, object] = {"family_id": str(family_id)}
            if custom_claims:
                combined_claims_new.update(custom_claims)
            private_key_override = (
                await self.uow.project_query_repo.get_private_key(command.project_id)
                if command.project_id
                else None
            )
            access_token = self._access_token.create(
                new_user,
                extra_claims=combined_claims_new,
                private_key_override=private_key_override,
            )

            await self._email_sender.send_welcome_email(
                new_user.email.value, 
                new_user.name,
                tenant_id=None,
                project_id=command.project_id,
            )

            return new_user, refresh_token, access_token, True, fallback_frontend_url
