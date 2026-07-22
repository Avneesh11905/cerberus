from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    RotateApiKeyCommand,
)
from src.modules.projects.application.dtos.project_dtos import RotateApiKeyDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class RotateApiKeyUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, api_key_adapter):
        self.uow = uow
        self.api_key_adapter = api_key_adapter
        super().__init__()
        self.api_key_adapter = api_key_adapter

    async def execute(self, command: RotateApiKeyCommand) -> RotateApiKeyDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            api_key_plaintext = self.api_key_adapter.generate(project.id)
            project.api_key_hash = self.api_key_adapter.hash(api_key_plaintext)
            project.updated_at = datetime.now(timezone.utc)
            await self.uow.project_command_repo.save(project)
            return RotateApiKeyDTO(api_key_plaintext=api_key_plaintext)
