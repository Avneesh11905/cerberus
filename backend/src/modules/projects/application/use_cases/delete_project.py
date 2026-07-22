from src.modules.projects.application.commands.project_commands import (
    DeleteProjectCommand,
)
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class DeleteProjectUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, command: DeleteProjectCommand) -> None:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            await self.uow.project_command_repo.delete(project.id)
