"""
Module: SQL Tenant Repository Adapter
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.superadmin.domain.repositories import TenantRepositoryPort
from src.modules.superadmin.domain.entities import TenantEntity
from src.modules.superadmin.infrastructure.models import Tenant

class SQLTenantRepositoryAdapter(TenantRepositoryPort[AsyncSession]):
    def _to_entity(self, orm_model: Tenant) -> TenantEntity:
        return TenantEntity.model_validate(orm_model)

    async def get_by_id(self, session: AsyncSession, tenant_id: UUID) -> TenantEntity | None:
        result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
        orm_model = result.scalars().first()
        if orm_model:
            return self._to_entity(orm_model)
        return None

    async def get_all(self, session: AsyncSession) -> Sequence[TenantEntity]:
        result = await session.execute(select(Tenant))
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]

    async def save(self, session: AsyncSession, tenant: TenantEntity) -> TenantEntity:
        result = await session.execute(select(Tenant).where(Tenant.id == tenant.id))
        orm_model = result.scalars().first()
        
        if orm_model:
            orm_model.is_active = tenant.is_active
            orm_model.role = tenant.role
            orm_model.name = tenant.name
        else:
            orm_model = Tenant(
                id=tenant.id,
                email=tenant.email,
                name=tenant.name,
                is_active=tenant.is_active,
                role=tenant.role,
                created_at=tenant.created_at
            )
            session.add(orm_model)
            
        await session.flush()
        return self._to_entity(orm_model)