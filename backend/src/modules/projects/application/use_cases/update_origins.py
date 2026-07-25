from datetime import datetime, UTC

from src.modules.projects.application.commands.project_commands import (
    UpdateOriginsCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateOriginsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class UpdateOriginsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, command: UpdateOriginsCommand) -> UpdateOriginsDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            project.allowed_origins = command.allowed_origins
            project.updated_at = datetime.now(UTC)
            return UpdateOriginsDTO(
                project=await self.uow.project_command_repo.save(project)
            )
