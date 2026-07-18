import secrets
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from src.modules.auth.application.ports.security.oauth_service import OAuthServicePort
from src.modules.auth.domain.exceptions import OAuthFailedException
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.shared.application.ports.api_key import ApiKeyPort


def _origin_from_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


class OAuthLoginUrlUserUseCase[SessionType, RequestType]:
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
        api_key: str | None = None,
        request_origin: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Returns a tuple of (authorization_url, session_data_to_store)
        """
        # Resolve project via API Key if pre-flight project_id isn't provided
        if not project_id and api_key:
            if not api_key.startswith("cerb_"):
                raise OAuthFailedException("Invalid API Key format")
            key_hash = self.api_key_adapter.hash(api_key)
            project = await self.project_query_repo.get_by_api_key_hash(
                session, key_hash
            )
            if not project:
                raise OAuthFailedException("Invalid API Key")
            project_id = project.id

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

        origin = _origin_from_url(request_origin)
        allowed_origins = {
            orig.rstrip("/") for orig in (project.allowed_origins or [])
        }
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
