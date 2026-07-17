from datetime import datetime, timezone
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectCommandRepositoryPort,
    ProjectQueryRepositoryPort,
)
from src.shared.application.ports import RsaKeyPort
from .base_project import BaseProjectUseCase


class RotateJwtSecretUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
        rsa_key_adapter: RsaKeyPort,
    ):
        super().__init__(query_repository)
        self.command_repository = command_repository
        self.rsa_key_adapter = rsa_key_adapter

    async def execute(
        self, session: SessionType, project_id: UUID, user_id: UUID
    ) -> str:
        project = await self._get_project_or_404(session, project_id, user_id)
        private_pem, public_pem = await self.rsa_key_adapter.generate_keypair()
        project.private_key = private_pem
        project.public_key = public_pem
        project.updated_at = datetime.now(timezone.utc)
        await self.command_repository.save(session, project)
        return public_pem
