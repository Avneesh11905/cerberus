from typing import Protocol

from src.modules.superadmin.domain.entities import SystemAnalyticsEntity


class SystemAnalyticsRepositoryPort[SessionType](Protocol):
    async def get_global_analytics(
        self, session: SessionType
    ) -> "SystemAnalyticsEntity": ...
