import secrets
from typing import Any

from src.modules.authentication.application.commands import (
    TenantOAuthLoginUrlQuery,
)
from src.modules.authentication.application.ports.security.oauth_service import (
    OAuthServicePort,
)
from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)


class TenantOAuthLoginUrlUseCase[SessionType, RequestType]:
    """
    Initiates the OAuth authorization flow for a Cerberus Dashboard tenant user.
    Generates the authorization URL and the required session state payload.
    Uses globally configured OAuth credentials (not project-specific).
    """

    def __init__(
        self,
        uow: AuthUoWPort,
        oauth_service: OAuthServicePort[Any],
    ):
        self.uow = uow
        self.oauth_service = oauth_service

    async def execute(
        self, command: TenantOAuthLoginUrlQuery
    ) -> tuple[str, dict[str, Any]]:
        async with self.uow:
            """
        Returns a tuple of (authorization_url, session_data_to_store)
        """
            nonce = secrets.token_urlsafe(16)
            session_data: dict[str, Any] = {"tenant_oauth_state": {"nonce": nonce}}

            # Let the service generate the URL
            url = await self.oauth_service.get_authorization_url(
                command.provider,
                None,
                command.request,
                command.redirect_uri,
                nonce,
                self.uow,
            )

            return url, session_data
