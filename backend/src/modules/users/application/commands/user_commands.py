from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateProfileCommand:
    user_id: UUID
    name: str | None = None
    picture: str | None = None
    receive_updates: bool | None = None


@dataclass(frozen=True)
class DeleteAccountCommand:
    user_id: UUID
    jwt_jti: str | None = None
    jwt_exp: int | None = None
