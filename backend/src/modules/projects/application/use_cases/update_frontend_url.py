from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    UpdateFrontendUrlCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateFrontendUrlDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.shared.domain.value_objects import HttpsUrl

from .base_project import BaseProjectUseCase


class UpdateFrontendUrlUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, command: UpdateFrontendUrlCommand) -> UpdateFrontendUrlDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            project.frontend_url = (
                HttpsUrl(command.frontend_url) if command.frontend_url else None
            )
            project.updated_at = datetime.now(timezone.utc)
            return UpdateFrontendUrlDTO(
                project=await self.uow.project_command_repo.save(project)
            )
