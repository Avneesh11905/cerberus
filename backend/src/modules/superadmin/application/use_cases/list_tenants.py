from collections.abc import Sequence

from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.domain.entities import TenantEntity


class ListTenantsUseCase:
    def __init__(self, uow: SuperAdminUoWPort):
        self.uow = uow

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[TenantEntity], int]:
        async with self.uow:
            tenants = await self.uow.tenant_repo.get_all(
                skip=skip, limit=limit, search=search
            )
            total = await self.uow.tenant_repo.count_all(search=search)
            return tenants, total
