import secrets
from typing import Any

from src.modules.authentication.application.commands import (
    ProjectUserOAuthLoginUrlQuery,
)
from src.modules.authentication.application.ports import OAuthServicePort
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.exceptions import OAuthFailedException
from src.shared.application.ports import ApiKeyPort
from src.shared.presentation.api.utils import origin_from_url


class ProjectUserOAuthLoginUrlUseCase[SessionType, RequestType]:
    """
    Initiates the OAuth authorization flow for an end-user of a specific tenant project.
    Generates the authorization URL and the required session state payload.
    """

    def __init__(
        self,
        uow: AuthUoWPort,
        api_key_adapter: ApiKeyPort,
        oauth_service: OAuthServicePort[Any],
    ):
        self.uow = uow
        self.api_key_adapter = api_key_adapter
        self.oauth_service = oauth_service

    async def execute(
        self, command: ProjectUserOAuthLoginUrlQuery
    ) -> tuple[str, dict[str, Any]]:
        async with self.uow:
            """
        Returns a tuple of (authorization_url, session_data_to_store)
        """
            if not command.project_id:
                raise OAuthFailedException(
                    "No project context found. Provide API key or use preflight flow."
                )

            project = await self.uow.project_query_repo.get_by_id(command.project_id)
            if not project:
                raise OAuthFailedException("Project not found")

            provider_config = project.oauth_config.get(command.provider, {})
            client_id = provider_config.get("client_id")
            client_secret_enc = provider_config.get("client_secret")
            if (
                not provider_config.get("enabled")
                or not client_id
                or not client_secret_enc
            ):
                raise OAuthFailedException("Provider not available")

            session_data: dict[str, Any] = {"oauth_project_id": str(command.project_id)}

            origin = origin_from_url(command.request_origin)
            allowed_origins = {
                orig.rstrip("/") for orig in (project.allowed_origins or [])
            }
            if origin and origin in allowed_origins:
                session_data["oauth_tenant_url"] = origin

            nonce = secrets.token_urlsafe(16)
            session_data["oauth_state"] = {
                "project_id": str(command.project_id),
                "nonce": nonce,
            }

            # Let the service generate the URL (and potentially mutate authlib request context if it needs to)
            url = await self.oauth_service.get_authorization_url(
                command.provider,
                command.project_id,
                command.request,
                command.redirect_uri,
                nonce,
                self.uow,
            )

            return url, session_data
