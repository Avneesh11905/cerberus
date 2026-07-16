from datetime import date
from typing import Protocol
from uuid import UUID

from src.modules.analytics.domain.entities import AnalyticsEvent


class AnalyticsRepositoryPort(Protocol):
    async def save_event(self, event: AnalyticsEvent) -> None:
        """Saves a raw analytics event."""
        ...

    async def get_project_metrics(
        self, project_id: UUID, start_date: date, end_date: date
    ) -> list:
        """Returns daily project metrics for a date range."""
        ...

    async def get_tenant_metrics(
        self, tenant_id: UUID, start_date: date, end_date: date
    ) -> list:
        """Returns daily tenant metrics for a date range."""
        ...
