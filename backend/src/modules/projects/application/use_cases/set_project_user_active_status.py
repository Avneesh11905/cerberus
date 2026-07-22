from src.modules.projects.application.commands.project_commands import (
    SetProjectUserActiveStatusCommand,
)
from src.modules.projects.application.dtos.project_dtos import (
    SetProjectUserActiveStatusDTO,
)
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.domain.exceptions import ProjectNotFoundError

from .base_project_user import BaseProjectUserUseCase


class SetProjectUserActiveStatusUseCase(BaseProjectUserUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(
        self, command: SetProjectUserActiveStatusCommand
    ) -> SetProjectUserActiveStatusDTO:
        async with self.uow:
            await self._verify_project_ownership(
                self.uow, command.project_id, command.tenant_id
            )
            user = await self.uow.project_user_repo.update_user_status(
                command.project_id, command.user_id, command.is_active
            )
            if not user:
                raise ProjectNotFoundError()
            return SetProjectUserActiveStatusDTO(user=user)
