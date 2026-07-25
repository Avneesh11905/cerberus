from datetime import datetime, UTC

from src.modules.projects.application.commands.project_commands import (
    UpdateEnvironmentCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateEnvironmentDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class UpdateEnvironmentUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, command: UpdateEnvironmentCommand) -> UpdateEnvironmentDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            project.environment = command.environment
            project.updated_at = datetime.now(UTC)
            return UpdateEnvironmentDTO(
                project=await self.uow.project_command_repo.save(project)
            )
