from uuid import UUID
from src.modules.superadmin.application.ports import TenantRepositoryPort
from src.modules.superadmin.domain.entities import TenantEntity
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.modules.auth.authorization.domain.enums import GlobalRole


class UpdateTenantGlobalRoleUseCase[SessionType]:
    def __init__(self, tenant_repository: TenantRepositoryPort):
        self.tenant_repository = tenant_repository

    async def execute(
        self, session: SessionType, tenant_id: UUID, role: GlobalRole
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

        tenant.role = role
        await self.tenant_repository.save(session, tenant)
        return tenant
