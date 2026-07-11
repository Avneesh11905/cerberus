"""
Module: Tenant Management Use Cases
"""

from typing import Sequence, TypeVar
from uuid import UUID

from src.modules.superadmin.domain.entities import TenantEntity, SystemLogEntity
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.modules.superadmin.domain.repositories import TenantRepositoryPort, SystemLogRepositoryPort

SessionType = TypeVar("SessionType")

class TenantManagementUseCase:
    def __init__(self, tenant_repository: TenantRepositoryPort, log_repository: SystemLogRepositoryPort):
        self.tenant_repository = tenant_repository
        self.log_repository = log_repository

    async def list_tenants(self, session: SessionType) -> Sequence[TenantEntity]:
        return await self.tenant_repository.get_all(session)

    async def update_status(self, session: SessionType, tenant_id: UUID, is_active: bool) -> TenantEntity:
        tenant = await self.tenant_repository.get_by_id(session, tenant_id)
        if not tenant:
            raise TenantNotFoundException()
        tenant.is_active = is_active
        await self.tenant_repository.save(session, tenant)
        return tenant

    async def update_role(self, session: SessionType, tenant_id: UUID, role: str) -> TenantEntity:
        tenant = await self.tenant_repository.get_by_id(session, tenant_id)
        if not tenant:
            raise TenantNotFoundException()
        tenant.role = role
        await self.tenant_repository.save(session, tenant)
        return tenant

    async def list_logs(self, session: SessionType, limit: int = 100) -> Sequence[SystemLogEntity]:
        return await self.log_repository.get_recent_logs(session, limit)