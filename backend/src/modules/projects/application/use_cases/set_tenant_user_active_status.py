from src.modules.projects.application.commands.project_commands import (
    SetTenantUserActiveStatusCommand,
)
from src.modules.projects.application.dtos.project_dtos import (
    SetTenantUserActiveStatusDTO,
)
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.domain.exceptions import ProjectNotFoundError

from .base_project_user import BaseProjectUserUseCase


class SetTenantUserActiveStatusUseCase(BaseProjectUserUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(
        self, command: SetTenantUserActiveStatusCommand
    ) -> SetTenantUserActiveStatusDTO:
        async with self.uow:
            users = await self.uow.project_user_repo.update_tenant_user_status(
                command.tenant_id, command.email, command.is_active
            )
            if not users:
                raise ProjectNotFoundError()
            return SetTenantUserActiveStatusDTO(users=users)
