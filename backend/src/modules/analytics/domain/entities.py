from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from src.shared.domain.enums import EventType


class AnalyticsEvent(BaseModel):
    id: UUID
    project_id: UUID | None = None
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict | None = None
