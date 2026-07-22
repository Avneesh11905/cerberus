from dataclasses import dataclass

from src.modules.authentication.domain.entities import UserIdentity


@dataclass(frozen=True)
class VerifyEmailResultDTO:
    identity: UserIdentity
    access_token: str
