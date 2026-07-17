from datetime import datetime, timezone
from uuid import UUID
from uuid6 import uuid7

from src.modules.projects.application.ports import (
    ProjectCommandRepositoryPort,
    ProjectQueryRepositoryPort,
)
from src.modules.projects.domain.entities import ProjectEntity
from src.shared.application.ports import ApiKeyPort, RsaKeyPort
from .base_project import BaseProjectUseCase


class CreateProjectUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
        api_key_adapter: ApiKeyPort,
        rsa_key_adapter: RsaKeyPort,
    ):
        super().__init__(query_repository)
        self.command_repository = command_repository
        self.api_key_adapter = api_key_adapter
        self.rsa_key_adapter = rsa_key_adapter

    async def execute(
        self, session: SessionType, user_id: UUID, name: str
    ) -> tuple[ProjectEntity, str, str]:
        project_id = uuid7()
        api_key_plaintext = self.api_key_adapter.generate(project_id)
        api_key_hash = self.api_key_adapter.hash(api_key_plaintext)
        private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()

        project = ProjectEntity(
            id=project_id,
            tenant_id=user_id,
            name=name,
            private_key=private_pem,
            public_key=public_pem,
            api_key_hash=api_key_hash,
            created_at=datetime.now(timezone.utc),
            environment="development",
        )
        saved_project = await self.command_repository.save(session, project)
        return saved_project, api_key_plaintext, public_pem
