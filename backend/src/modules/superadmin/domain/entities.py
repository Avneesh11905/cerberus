from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.auth.domain.user import UserRole

class TenantEntity(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemLogEntity(BaseModel):
    id: UUID
    level: str
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
