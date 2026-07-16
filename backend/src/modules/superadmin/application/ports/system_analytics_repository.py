from typing import Generic, Protocol, TypeVar

from src.modules.superadmin.domain.entities import SystemAnalyticsEntity

SessionType = TypeVar("SessionType", contravariant=True)


class SystemAnalyticsRepositoryPort(Protocol, Generic[SessionType]):
    async def get_global_analytics(
        self, session: SessionType
    ) -> "SystemAnalyticsEntity": ...
