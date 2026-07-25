from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.modules.authorization.domain.enums import GlobalRole


class TenantRes(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    role: GlobalRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def extract_email(cls, v: Any) -> str:
        if hasattr(v, "value"):
            return v.value
        return v

    @field_validator("name", mode="before")
    @classmethod
    def extract_name(cls, v: Any) -> str | None:
        if hasattr(v, "value"):
            return v.value
        return v
