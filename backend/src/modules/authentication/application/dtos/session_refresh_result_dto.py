from dataclasses import dataclass

from src.modules.authentication.domain.entities import UserIdentity


@dataclass(frozen=True)
class SessionRefreshResultDTO:
    identity: UserIdentity
    access_token: str
    refresh_token: str
    was_compromised: bool
