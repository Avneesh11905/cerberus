import secrets
from typing import Any
from uuid import UUID
from src.shared.api.utils import origin_from_url
from src.modules.auth.authentication.domain.exceptions import OAuthFailedException
from src.modules.auth.authentication.application.ports import OAuthServicePort
from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.shared.application.ports import ApiKeyPort


class ProjectUserOAuthLoginUrlUseCase[SessionType, RequestType]:
    """
    Initiates the OAuth authorization flow for an end-user of a specific tenant project.
    Generates the authorization URL and the required session state payload.
    """

    def __init__(
        self,
        project_query_repo: ProjectQueryRepositoryPort[SessionType],
        api_key_adapter: ApiKeyPort,
        oauth_service: OAuthServicePort[SessionType, RequestType],
    ):
        self.project_query_repo = project_query_repo
        self.api_key_adapter = api_key_adapter
        self.oauth_service = oauth_service

    async def execute(
        self,
        session: SessionType,
        request: RequestType,
        provider: str,
        redirect_uri: str,
        project_id: UUID | None = None,
        request_origin: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Returns a tuple of (authorization_url, session_data_to_store)
        """
        if not project_id:
            raise OAuthFailedException(
                "No project context found. Provide API key or use preflight flow."
            )

        project = await self.project_query_repo.get_by_id(session, project_id)
        if not project:
            raise OAuthFailedException("Project not found")

        provider_config = project.oauth_config.get(provider, {})
        client_id = provider_config.get("client_id")
        client_secret_enc = provider_config.get("client_secret")
        if not provider_config.get("enabled") or not client_id or not client_secret_enc:
            raise OAuthFailedException("Provider not available")

        session_data: dict[str, Any] = {"oauth_project_id": str(project_id)}

        origin = origin_from_url(request_origin)
        allowed_origins = {orig.rstrip("/") for orig in (project.allowed_origins or [])}
        if origin and origin in allowed_origins:
            session_data["oauth_tenant_url"] = origin

        nonce = secrets.token_urlsafe(16)
        session_data["oauth_state"] = {
            "project_id": str(project_id),
            "nonce": nonce,
        }

        # Let the service generate the URL (and potentially mutate authlib request context if it needs to)
        url = await self.oauth_service.get_authorization_url(
            provider, project_id, request, redirect_uri, nonce, session
        )

        return url, session_data
