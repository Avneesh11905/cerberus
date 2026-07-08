from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TenantRes(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TenantStatusUpdateReq(BaseModel):
    is_active: bool


class SystemLogRes(BaseModel):
    id: UUID
    level: str
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
