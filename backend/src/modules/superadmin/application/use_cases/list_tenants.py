from typing import Sequence
from src.modules.superadmin.application.ports import TenantRepositoryPort
from src.modules.superadmin.domain.entities import TenantEntity


class ListTenantsUseCase[SessionType]:
    def __init__(self, tenant_repository: TenantRepositoryPort):
        self.tenant_repository = tenant_repository

    async def execute(
        self,
        session: SessionType,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[TenantEntity], int]:
        tenants = await self.tenant_repository.get_all(
            session, skip=skip, limit=limit, search=search
        )
        total = await self.tenant_repository.count_all(session, search=search)
        return tenants, total
