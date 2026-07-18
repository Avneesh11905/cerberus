from uuid import UUID

from src.modules.auth.authentication.domain.exceptions import OAuthFailedException
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.shared.application.ports.api_key import ApiKeyPort


class ValidateOAuthProviderUseCase[SessionType]:
    """
    Validates an API key and ensures the requested OAuth provider is correctly
    configured before redirecting the user to the provider login URL.
    """

    def __init__(
        self,
        project_query_repo: ProjectQueryRepositoryPort[SessionType],
        api_key_adapter: ApiKeyPort,
    ):
        self.project_query_repo = project_query_repo
        self.api_key_adapter = api_key_adapter

    async def execute(self, session: SessionType, provider: str, api_key: str) -> UUID:
        if not api_key.startswith("cerb_"):
            raise OAuthFailedException("Invalid API Key format")

        key_hash = self.api_key_adapter.hash(api_key)
        project = await self.project_query_repo.get_by_api_key_hash(session, key_hash)
        if not project:
            raise OAuthFailedException("Invalid API Key")

        provider_config = project.oauth_config.get(provider, {})
        client_id = provider_config.get("client_id")
        client_secret_enc = provider_config.get("client_secret")

        if not provider_config.get("enabled") or not client_id or not client_secret_enc:
            raise OAuthFailedException("Provider not available")

        return project.id
