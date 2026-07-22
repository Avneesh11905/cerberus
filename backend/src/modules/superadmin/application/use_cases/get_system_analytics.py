from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.domain.entities import SystemAnalyticsEntity


class GetSystemAnalyticsUseCase:
    def __init__(self, uow: SuperAdminUoWPort):
        self.uow = uow

    async def execute(
        self,
    ) -> SystemAnalyticsEntity:
        async with self.uow:
            return await self.uow.analytics_repo.get_global_analytics()
