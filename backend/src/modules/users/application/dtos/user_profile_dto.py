from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserProfileDTO:
    id: UUID
    email: str
    receive_updates: bool
    login_methods: list[str]
    role: str | None = None
    name: str | None = None
    picture: str | None = None
