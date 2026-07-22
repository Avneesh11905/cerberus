from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import UpdateNameCommand
from src.modules.projects.application.dtos.project_dtos import UpdateNameDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class UpdateNameUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, command: UpdateNameCommand) -> UpdateNameDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            project.name = command.name
            project.updated_at = datetime.now(timezone.utc)
            return UpdateNameDTO(
                project=await self.uow.project_command_repo.save(project)
            )
