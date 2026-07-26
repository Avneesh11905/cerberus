from src.modules.analytics.application.dtos.metrics_dtos import TenantMetricsDTO
from src.modules.analytics.application.ports.analytics_unit_of_work import (
    AnalyticsUoWPort,
)
from src.modules.analytics.application.queries.metrics_queries import (
    GetTenantMetricsQuery,
)


class GetTenantMetricsUseCase:
    def __init__(self, uow: AnalyticsUoWPort):
        self.uow = uow

    async def execute(self, query: GetTenantMetricsQuery) -> TenantMetricsDTO:
        async with self.uow:
            result = await self.uow.analytics_repo.get_tenant_metrics(
                query.tenant_id, query.start_date, query.end_date
            )
            return TenantMetricsDTO(metrics=result["metrics"], totals=result["totals"])
