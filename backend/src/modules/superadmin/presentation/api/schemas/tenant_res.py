from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from src.modules.authorization.domain.enums import GlobalRole


class TenantRes(BaseModel):
    id: UUID
    email: str
    name: str | None
    is_active: bool
    role: GlobalRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def extract_email(cls, v: object) -> str:
        if hasattr(v, "value"):
            return str(getattr(v, "value"))
        return str(v)

    @field_validator("name", mode="before")
    @classmethod
    def extract_name(cls, v: object) -> str | None:
        if hasattr(v, "value"):
            val = getattr(v, "value")
            return str(val) if val is not None else None
        return v if v is None else str(v)
