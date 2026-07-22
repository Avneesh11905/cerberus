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


class UpdateTenantGlobalRoleUseCase:
    def __init__(self, uow: SuperAdminUoWPort):
        self.uow = uow

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
            return UpdateTenantGlobalRoleDTO(tenant=tenant)
