from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    RotateJwtSecretCommand,
)
from src.modules.projects.application.dtos.project_dtos import RotateJwtSecretDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class RotateJwtSecretUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, rsa_key_adapter):
        self.uow = uow
        self.rsa_key_adapter = rsa_key_adapter
        super().__init__()
        self.rsa_key_adapter = rsa_key_adapter

    async def execute(self, command: RotateJwtSecretCommand) -> RotateJwtSecretDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )
            private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()
            project.private_key = private_pem
            project.public_key = public_pem
            project.updated_at = datetime.now(timezone.utc)
            await self.uow.project_command_repo.save(project)
            return RotateJwtSecretDTO(public_pem=public_pem)
