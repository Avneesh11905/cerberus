from dataclasses import dataclass

from src.modules.authentication.domain.entities import UserIdentity


@dataclass(frozen=True)
class OAuthExchangeResultDTO:
    identity: UserIdentity
    access_token: str
    refresh_token: str
    is_new_user: bool
