from uuid import UUID

from fastapi import Request

from src.modules.authentication.application.ports.security.oauth_service import (
    OAuthServicePort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.entities import OAuthUserInfo
from src.modules.authentication.domain.exceptions import OAuthFailedException
from src.modules.authentication.infrastructure.oauth import PARSERS, PROVIDERS
from src.modules.authentication.infrastructure.oauth.dynamic import (
    get_dynamic_oauth_client,
)
from src.shared.application.ports.encryption import EncryptionPort


class OAuthServiceAdapter(OAuthServicePort[Request]):
    def __init__(self, encryption_adapter: EncryptionPort):
        self.encryption_adapter = encryption_adapter

    async def get_authorization_url(
        self,
        provider: str,
        project_id: UUID | None,
        request: Request,
        redirect_uri: str,
        state: str,
        uow: AuthUoWPort,
    ) -> str:
        client = await self._get_client(provider, project_id, uow)
        response = await client.authorize_redirect(request, redirect_uri, state=state)
        return response.headers["location"]

    async def exchange_code_for_user_info(
        self,
        provider: str,
        project_id: UUID | None,
        request: Request,
        uow: AuthUoWPort,
    ) -> OAuthUserInfo:
        client = await self._get_client(provider, project_id, uow)

        # Exchanges the code and retrieves tokens.
        token = await client.authorize_access_token(request)

        # Uses the registry parsers to map provider-specific info to our internal model.
        parser = PARSERS.get(provider)
        if not parser:
            raise OAuthFailedException(f"No parser registered for provider: {provider}")

        user_info = await parser(client, token)
        return user_info

    async def _get_client(
        self, provider: str, project_id: UUID | None, uow: AuthUoWPort
    ):
        if not project_id:
            # Tenant login uses global static config
            client = PROVIDERS.get(provider)
            if not client:
                raise OAuthFailedException(f"Invalid tenant provider: {provider}")
            return client

        # Project end-user login uses dynamic config
        project = await uow.project_query_repo.get_by_id(project_id)
        if not project:
            raise OAuthFailedException("Project not found")

        provider_config = project.oauth_config.get(provider, {})
        client_id = provider_config.get("client_id")
        client_secret_enc = provider_config.get("client_secret")

        if not provider_config.get("enabled") or not client_id or not client_secret_enc:
            raise OAuthFailedException("OAuth provider not enabled or configured")

        client_secret = self.encryption_adapter.decrypt(client_secret_enc)
        return get_dynamic_oauth_client(provider, client_id, client_secret)
