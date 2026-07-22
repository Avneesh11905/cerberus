from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionResponse(BaseModel):
    family_id: UUID
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_active: datetime
    is_current: bool
    auth_provider: str


class RefreshResponse(BaseModel):
    access_token: str
    csrf_token: str | None = None
