"""
Module: SQL Tenant Repository Adapter
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.superadmin.application.ports import TenantRepositoryPort
from src.modules.superadmin.domain.entities import TenantEntity
from src.modules.superadmin.infrastructure.models import Tenant


class SQLTenantRepositoryAdapter(TenantRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, orm_model: Tenant) -> TenantEntity:

        from src.shared.domain.value_objects import EmailAddress, PersonName

        return TenantEntity(
            id=orm_model.id,
            email=EmailAddress(orm_model.email),
            name=PersonName(str(orm_model.name))
            if getattr(orm_model, "name", None)
            else None,
            is_active=orm_model.is_active,
            role=orm_model.role,
            created_at=orm_model.created_at,
        )

    async def get_by_id(self, tenant_id: UUID) -> TenantEntity | None:
        result = await self._session.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        orm_model = result.scalars().first()
        if orm_model:
            return self._to_entity(orm_model)
        return None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[TenantEntity]:
        from sqlalchemy import or_, String

        stmt = select(Tenant)

        if search:
            stmt = stmt.where(
                or_(
                    Tenant.email.ilike(f"%{search}%"),
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.role.cast(String).ilike(f"%{search}%"),
                )
            )

        stmt = stmt.order_by(Tenant.email.asc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]

    async def count_all(self, search: str | None = None) -> int:
        from sqlalchemy import func, or_, String

        stmt = select(func.count(Tenant.id))

        if search:
            stmt = stmt.where(
                or_(
                    Tenant.email.ilike(f"%{search}%"),
                    Tenant.name.ilike(f"%{search}%"),
                    Tenant.role.cast(String).ilike(f"%{search}%"),
                )
            )

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def save(self, tenant: TenantEntity) -> TenantEntity:
        result = await self._session.execute(
            select(Tenant).where(Tenant.id == tenant.id)
        )
        orm_model = result.scalars().first()

        if orm_model:
            orm_model.is_active = tenant.is_active
            orm_model.role = tenant.role
            orm_model.name = tenant.name.value if tenant.name else None
        else:
            orm_model = Tenant(
                id=tenant.id,
                email=tenant.email.value,
                name=tenant.name.value if tenant.name else None,
                is_active=tenant.is_active,
                role=tenant.role,
                created_at=tenant.created_at,
            )
            self._session.add(orm_model)

        await self._session.flush()
        return self._to_entity(orm_model)
