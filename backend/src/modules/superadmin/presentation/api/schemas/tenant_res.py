from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.authorization.domain.enums import GlobalRole


class TenantRes(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    role: GlobalRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
