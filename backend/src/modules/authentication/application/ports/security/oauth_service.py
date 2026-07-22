from typing import Protocol
from uuid import UUID

from src.modules.authentication.application.ports.authentication_unit_of_work import (
    AuthUoWPort,
)
from src.modules.authentication.domain.entities import OAuthUserInfo


class OAuthServicePort[RequestType](Protocol):
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
        uow: AuthUoWPort,
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
        uow: AuthUoWPort,
    ) -> OAuthUserInfo:
        """
        Exchanges the authorization code inside the request for UserInfo.
        """
        ...
