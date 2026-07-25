from dataclasses import dataclass, field
from datetime import datetime
from collections.abc import Mapping
from uuid import UUID

from src.shared.domain.value_objects import HttpsUrl
from src.shared.domain.types import JsonValue


@dataclass(kw_only=True)
class ProjectEntity:
    """Pure domain entity representing a Tenant's Project."""

    id: UUID
    tenant_id: UUID
    name: str
    private_key: str
    public_key: str
    api_key_hash: str
    created_at: datetime

    oauth_config: dict = field(default_factory=dict)
    allowed_origins: list[str] = field(default_factory=list)
    default_claims: Mapping[str, JsonValue] | None = None
    environment: str = "development"
    frontend_url: HttpsUrl | None = None
    updated_at: datetime | None = None
