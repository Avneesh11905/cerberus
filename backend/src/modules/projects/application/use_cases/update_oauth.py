from datetime import datetime, timezone

from src.modules.projects.application.commands.project_commands import (
    UpdateOauthCommand,
)
from src.modules.projects.application.dtos.project_dtos import UpdateOauthDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort

from .base_project import BaseProjectUseCase


class UpdateOauthUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, encryption_adapter):
        self.uow = uow
        self.encryption_adapter = encryption_adapter
        super().__init__()
        self.encryption_adapter = encryption_adapter

    async def execute(self, command: UpdateOauthCommand) -> UpdateOauthDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, command.project_id, command.user_id
            )

            for provider, config in command.incoming_config.items():
                if "client_secret" in config and config["client_secret"]:
                    config["client_secret"] = self.encryption_adapter.encrypt(
                        config["client_secret"]
                    )

            project.oauth_config = command.incoming_config
            project.updated_at = datetime.now(timezone.utc)
            return UpdateOauthDTO(
                project=await self.uow.project_command_repo.save(project)
            )
