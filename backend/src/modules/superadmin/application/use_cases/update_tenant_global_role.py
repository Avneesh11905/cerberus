from src.modules.superadmin.application.commands.superadmin_commands import (
    UpdateTenantGlobalRoleCommand,
)
from src.modules.superadmin.application.dtos.superadmin_dtos import (
    UpdateTenantGlobalRoleDTO,
)
from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.domain.exceptions import TenantNotFoundException


from src.shared.application.ports import CachePort
import time


class UpdateTenantGlobalRoleUseCase:
    def __init__(self, uow: SuperAdminUoWPort, cache: CachePort | None = None):
        self.uow = uow
        self.cache = cache

    async def execute(
        self, command: UpdateTenantGlobalRoleCommand
    ) -> UpdateTenantGlobalRoleDTO:
        async with self.uow:
            from src.core.config import get_settings

            tenant = await self.uow.tenant_repo.get_by_id(command.tenant_id)
            if not tenant:
                raise TenantNotFoundException()

            if tenant.email == get_settings().core.SUPERADMIN_EMAIL:
                from src.modules.superadmin.domain.exceptions import (
                    AbsoluteSuperadminImmutableException,
                )

                raise AbsoluteSuperadminImmutableException()

            tenant.role = command.role
            await self.uow.tenant_repo.save(tenant)

            if self.cache:
                await self.cache.set_string(
                    f"role_updated:{command.tenant_id}",
                    str(time.time()),
                    ttl=86400 * 30,
                )

            return UpdateTenantGlobalRoleDTO(tenant=tenant)
