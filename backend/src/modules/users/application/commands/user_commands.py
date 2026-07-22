from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class UpdateProfileCommand:
    user_id: UUID
    name: Optional[str] = None
    picture: Optional[str] = None
    receive_updates: Optional[bool] = None


@dataclass(frozen=True)
class DeleteAccountCommand:
    user_id: UUID
    jwt_jti: Optional[str] = None
    jwt_exp: Optional[int] = None
