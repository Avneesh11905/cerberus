from typing import Protocol, Sequence
from uuid import UUID

from src.modules.superadmin.domain.entities import TenantEntity


class TenantRepositoryPort[SessionType](Protocol):
    async def get_by_id(
        self, session: SessionType, tenant_id: UUID
    ) -> TenantEntity | None: ...

    async def get_all(
        self,
        session: SessionType,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[TenantEntity]: ...

    async def count_all(
        self, session: SessionType, search: str | None = None
    ) -> int: ...

    async def save(
        self, session: SessionType, tenant: TenantEntity
    ) -> TenantEntity: ...
