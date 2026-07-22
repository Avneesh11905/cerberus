from typing import Protocol

from src.modules.superadmin.domain.entities import SystemAnalyticsEntity


class SystemAnalyticsRepositoryPort(Protocol):
    async def get_global_analytics(
        self,
    ) -> "SystemAnalyticsEntity": ...
