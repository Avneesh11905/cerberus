from datetime import date
from uuid import UUID

from src.modules.analytics.application.ports.analytics_repository import (
    AnalyticsRepositoryPort,
)


class QueryAnalyticsUseCase:
    def __init__(self, repository: AnalyticsRepositoryPort):
        self.repository = repository

    async def get_project_metrics(
        self, project_id: UUID, start_date: date, end_date: date
    ) -> list:
        return await self.repository.get_project_metrics(
            project_id, start_date, end_date
        )

    async def get_tenant_metrics(
        self, tenant_id: UUID, start_date: date, end_date: date
    ) -> list:
        return await self.repository.get_tenant_metrics(tenant_id, start_date, end_date)
