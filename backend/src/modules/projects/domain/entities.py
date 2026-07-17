from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectEntity(BaseModel):
    """Pure domain entity representing a Tenant's Project."""

    id: UUID
    tenant_id: UUID
    name: str
    private_key: str
    public_key: str
    api_key_hash: str
    created_at: datetime

    admin_email: str | None = None
    oauth_config: dict = Field(default_factory=dict)
    allowed_origins: list[str] = Field(default_factory=list)
    environment: str = "development"
    frontend_url: str | None = None
    updated_at: datetime | None = None
