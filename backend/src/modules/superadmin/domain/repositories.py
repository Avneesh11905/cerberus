from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar
from uuid import UUID

from src.modules.superadmin.domain.entities import TenantEntity, SystemLogEntity

SessionType = TypeVar("SessionType")

class TenantRepositoryPort(ABC, Generic[SessionType]):
    @abstractmethod
    async def get_by_id(self, session: SessionType, tenant_id: UUID) -> TenantEntity | None:
        pass

    @abstractmethod
    async def get_all(self, session: SessionType) -> Sequence[TenantEntity]:
        pass

    @abstractmethod
    async def save(self, session: SessionType, tenant: TenantEntity) -> TenantEntity:
        pass


class SystemLogRepositoryPort(ABC, Generic[SessionType]):
    @abstractmethod
    async def get_recent_logs(self, session: SessionType, limit: int = 100) -> Sequence[SystemLogEntity]:
        pass
