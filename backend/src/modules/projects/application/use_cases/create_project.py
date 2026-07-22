from datetime import datetime, timezone

from uuid6 import uuid7

from src.modules.projects.application.commands.project_commands import (
    CreateProjectCommand,
)
from src.modules.projects.application.dtos.project_dtos import CreateProjectDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.domain.entities import ProjectEntity

from .base_project import BaseProjectUseCase


class CreateProjectUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort, api_key_adapter, rsa_key_adapter):
        self.uow = uow
        self.api_key_adapter = api_key_adapter
        self.rsa_key_adapter = rsa_key_adapter
        super().__init__()
        self.api_key_adapter = api_key_adapter
        self.rsa_key_adapter = rsa_key_adapter

    async def execute(self, command: CreateProjectCommand) -> CreateProjectDTO:
        async with self.uow:
            project_id = uuid7()
            api_key_plaintext = self.api_key_adapter.generate(project_id)
            api_key_hash = self.api_key_adapter.hash(api_key_plaintext)
            private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()

            project = ProjectEntity(
                id=project_id,
                tenant_id=command.user_id,
                name=command.name,
                private_key=private_pem,
                public_key=public_pem,
                api_key_hash=api_key_hash,
                created_at=datetime.now(timezone.utc),
                environment="development",
            )
            saved_project = await self.uow.project_command_repo.save(project)
            return CreateProjectDTO(
                project=saved_project,
                api_key_plaintext=api_key_plaintext,
                public_pem=public_pem,
            )
