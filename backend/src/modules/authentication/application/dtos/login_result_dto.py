from dataclasses import dataclass
from typing import Optional

from src.modules.authentication.domain.entities import UserIdentity


@dataclass(frozen=True)
class LoginResultDTO:
    identity: Optional[UserIdentity]
    access_token: str
    refresh_token: str
