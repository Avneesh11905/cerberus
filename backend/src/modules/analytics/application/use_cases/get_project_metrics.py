from src.modules.analytics.application.dtos.metrics_dtos import ProjectMetricsDTO
from src.modules.analytics.application.ports.analytics_unit_of_work import (
    AnalyticsUoWPort,
)
from src.modules.analytics.application.queries.metrics_queries import (
    GetProjectMetricsQuery,
)


class GetProjectMetricsUseCase:
    def __init__(self, uow: AnalyticsUoWPort):
        self.uow = uow

    async def execute(self, query: GetProjectMetricsQuery) -> ProjectMetricsDTO:
        async with self.uow:
            data = await self.uow.analytics_repo.get_project_metrics(
                query.project_id, query.start_date, query.end_date
            )
            return ProjectMetricsDTO(data=data)
