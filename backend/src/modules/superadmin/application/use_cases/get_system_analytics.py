from src.modules.superadmin.application.ports import SystemAnalyticsRepositoryPort
from src.modules.superadmin.domain.entities import SystemAnalyticsEntity


class GetSystemAnalyticsUseCase[SessionType]:
    def __init__(self, analytics_repository: SystemAnalyticsRepositoryPort):
        self.analytics_repository = analytics_repository

    async def execute(self, session: SessionType) -> SystemAnalyticsEntity:
        return await self.analytics_repository.get_global_analytics(session)
