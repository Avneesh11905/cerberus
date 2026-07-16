"""
Module: SQL Tenant Repository Adapter
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.superadmin.domain.entities import TenantEntity
from src.modules.superadmin.infrastructure.models import Tenant


from src.modules.superadmin.application.ports import TenantRepositoryPort


class SQLTenantRepositoryAdapter(TenantRepositoryPort[AsyncSession]):
    def _to_entity(self, orm_model: Tenant) -> TenantEntity:
        return TenantEntity.model_validate(orm_model)

    async def get_by_id(
        self, session: AsyncSession, tenant_id: UUID
    ) -> TenantEntity | None:
        result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
        orm_model = result.scalars().first()
        if orm_model:
            return self._to_entity(orm_model)
        return None

    async def get_all(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[TenantEntity]:
        from sqlalchemy import or_

        stmt = select(Tenant)

        if search:
            stmt = stmt.where(
                or_(
                    Tenant.email.ilike(f"%{search}%"),
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.role.cast(str).ilike(f"%{search}%"),
                )
            )

        stmt = stmt.order_by(Tenant.email.asc()).offset(skip).limit(limit)
        result = await session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]

    async def count_all(self, session: AsyncSession, search: str | None = None) -> int:
        from sqlalchemy import func, or_

        stmt = select(func.count(Tenant.id))

        if search:
            stmt = stmt.where(
                or_(
                    Tenant.email.ilike(f"%{search}%"),
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.role.cast(str).ilike(f"%{search}%"),
                )
            )

        result = await session.execute(stmt)
        return result.scalar_one() or 0

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
                created_at=tenant.created_at,
            )
            session.add(orm_model)

        await session.flush()
        return self._to_entity(orm_model)
