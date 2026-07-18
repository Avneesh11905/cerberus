import secrets
from typing import Any

from src.modules.auth.authentication.application.ports.security.oauth_service import (
    OAuthServicePort,
)


class TenantOAuthLoginUrlUseCase[SessionType, RequestType]:
    """
    Initiates the OAuth authorization flow for a Cerberus Dashboard tenant user.
    Generates the authorization URL and the required session state payload.
    Uses globally configured OAuth credentials (not project-specific).
    """

    def __init__(
        self,
        oauth_service: OAuthServicePort[SessionType, RequestType],
    ):
        self.oauth_service = oauth_service

    async def execute(
        self,
        session: SessionType,
        request: RequestType,
        provider: str,
        redirect_uri: str,
    ) -> tuple[str, dict[str, Any]]:
        """
        Returns a tuple of (authorization_url, session_data_to_store)
        """
        nonce = secrets.token_urlsafe(16)
        session_data: dict[str, Any] = {"tenant_oauth_state": {"nonce": nonce}}

        # Let the service generate the URL
        url = await self.oauth_service.get_authorization_url(
            provider, None, request, redirect_uri, nonce, session
        )

        return url, session_data
