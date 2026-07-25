from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SessionDTO:
    id: UUID
    ip_address: str | None
    user_agent: str | None
    device_name: str | None
    os_name: str | None
    city: str | None
    country: str | None
    is_current: bool
    created_at: int
    last_active: int
    expires_at: int
