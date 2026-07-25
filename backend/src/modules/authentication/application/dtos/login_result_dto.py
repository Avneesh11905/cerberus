from dataclasses import dataclass

from src.modules.authentication.domain.entities import UserIdentity


@dataclass(frozen=True)
class LoginResultDTO:
    identity: UserIdentity | None
    access_token: str
    refresh_token: str
