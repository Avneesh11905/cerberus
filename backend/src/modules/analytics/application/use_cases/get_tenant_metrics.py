from datetime import date
from uuid import UUID

from src.modules.analytics.application.ports import (
    AnalyticsRepositoryPort,
)


class GetTenantMetricsUseCase:
    def __init__(self, repository: AnalyticsRepositoryPort):
        self.repository = repository

    async def execute(self, tenant_id: UUID, start_date: date, end_date: date) -> list:
        return await self.repository.get_tenant_metrics(tenant_id, start_date, end_date)
