from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class SessionDTO:
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_name: Optional[str]
    os_name: Optional[str]
    city: Optional[str]
    country: Optional[str]
    is_current: bool
    created_at: int
    last_active: int
    expires_at: int
