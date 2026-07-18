from typing import Protocol
from uuid import UUID

from src.modules.auth.domain.entities import OAuthUserInfo


class OAuthServicePort[SessionType, RequestType](Protocol):
    """
    Abstract port for all OAuth operations.
    """

    async def get_authorization_url(
        self,
        provider: str,
        project_id: UUID | None,
        request: RequestType,
        redirect_uri: str,
        state: str,
        session: SessionType,
    ) -> str:
        """
        Returns the OAuth authorization URL for the given provider.
        """
        ...

    async def exchange_code_for_user_info(
        self,
        provider: str,
        project_id: UUID | None,
        request: RequestType,
        session: SessionType,
    ) -> OAuthUserInfo:
        """
        Exchanges the authorization code inside the request for UserInfo.
        """
        ...
