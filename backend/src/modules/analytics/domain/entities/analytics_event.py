from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from src.shared.domain.enums import EventType


@dataclass(kw_only=True)
class AnalyticsEvent:
    id: UUID
    project_id: UUID | None = None
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    event_type: EventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict | None = None
