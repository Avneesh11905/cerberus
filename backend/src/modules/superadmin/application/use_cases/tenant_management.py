"""
Module: Tenant Management Use Cases
"""

from typing import Sequence, TypeVar
from uuid import UUID

from src.modules.auth.application.ports import RefreshTokenRepositoryPort
from src.modules.superadmin.domain.entities import (
    SystemAnalyticsEntity,
    SystemLogEntity,
    TenantEntity,
)
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.modules.superadmin.application.ports import (
    SystemAnalyticsRepositoryPort,
    SystemLogRepositoryPort,
    TenantRepositoryPort,
)
from src.shared.application.ports.cache import CachePort
from src.shared.application.ports.uow import UoWPort
from src.shared.domain.enums import UserRole

SessionType = TypeVar("SessionType")


class TenantManagementUseCase:
    def __init__(
        self,
        tenant_repository: TenantRepositoryPort,
        log_repository: SystemLogRepositoryPort,
        analytics_repository: SystemAnalyticsRepositoryPort,
        refresh_repo: RefreshTokenRepositoryPort | None = None,
        cache: CachePort | None = None,
    ):
        self.tenant_repository = tenant_repository
        self.log_repository = log_repository
        self.analytics_repository = analytics_repository
        self.refresh_repo = refresh_repo
        self.cache = cache

    async def get_system_analytics(self, session: SessionType) -> SystemAnalyticsEntity:
        return await self.analytics_repository.get_global_analytics(session)

    async def list_tenants(
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

    async def update_status(
        self, uow: UoWPort[SessionType], tenant_id: UUID, is_active: bool
    ) -> TenantEntity:
        tenant = await self.tenant_repository.get_by_id(uow.session, tenant_id)
        if not tenant:
            raise TenantNotFoundException()
        tenant.is_active = is_active
        await self.tenant_repository.save(uow.session, tenant)

        if not is_active:
            if self.refresh_repo:
                await self.refresh_repo.revoke_all_for_user(uow.session, tenant_id)
            if self.cache:
                await self.cache.set_string(
                    f"disabled_user:{tenant_id}", "1", ttl=86400 * 30
                )
        else:
            if self.cache:
                await self.cache.delete_key(f"disabled_user:{tenant_id}")

        return tenant

    async def update_role(
        self, session: SessionType, tenant_id: UUID, role: str
    ) -> TenantEntity:
        from src.core.config import core_settings

        tenant = await self.tenant_repository.get_by_id(session, tenant_id)
        if not tenant:
            raise TenantNotFoundException()

        if tenant.email == core_settings.SUPERADMIN_EMAIL:
            from src.modules.superadmin.domain.exceptions import (
                AbsoluteSuperadminImmutableException,
            )

            raise AbsoluteSuperadminImmutableException()

        tenant.role = UserRole(role)
        await self.tenant_repository.save(session, tenant)
        return tenant

    async def list_logs(
        self,
        session: SessionType,
        skip: int = 0,
        limit: int = 100,
        level: str | None = None,
    ) -> tuple[Sequence[SystemLogEntity], int]:
        from src.shared.domain.enums import LogLevel

        parsed_level = LogLevel(level) if level else None
        logs = await self.log_repository.get_recent_logs(
            session, skip=skip, limit=limit, level=parsed_level
        )
        total = await self.log_repository.count_logs(session, level=parsed_level)
        return logs, total
