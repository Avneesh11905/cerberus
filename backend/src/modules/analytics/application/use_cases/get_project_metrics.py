from datetime import date
from uuid import UUID

from src.modules.analytics.application.ports import (
    AnalyticsRepositoryPort,
)


class GetProjectMetricsUseCase:
    def __init__(self, repository: AnalyticsRepositoryPort):
        self.repository = repository

    async def execute(self, project_id: UUID, start_date: date, end_date: date) -> list:
        return await self.repository.get_project_metrics(
            project_id, start_date, end_date
        )
