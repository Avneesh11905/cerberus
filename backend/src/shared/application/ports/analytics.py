from typing import Protocol
from uuid import UUID
from pydantic import JsonValue


class AnalyticsEventPort(Protocol):
    """
    Port for asynchronously emitting usage and analytics events.
    Events should be handled by a dedicated background queue.
    """

    def record_event(
        self,
        event_type: str,
        event_id: UUID | None = None,
        project_id: UUID | None = None,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        metadata: dict[str, JsonValue] | None = None,
    ) -> None:
        """
        Record a generic analytics event.
        """
        ...
