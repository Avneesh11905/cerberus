from typing import Any, Protocol
from uuid import UUID


class AnalyticsEventPort(Protocol):
    """
    Port for asynchronously emitting usage and analytics events.
    Events should be handled by a dedicated background queue.
    """

    def record_event(
        self,
        event_type: str,
        project_id: UUID | None = None,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a generic analytics event.
        """
        ...
