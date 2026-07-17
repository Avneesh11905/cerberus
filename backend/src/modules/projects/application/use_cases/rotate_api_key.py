from datetime import datetime, timezone
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectCommandRepositoryPort,
    ProjectQueryRepositoryPort,
)
from src.shared.application.ports import ApiKeyPort
from .base_project import BaseProjectUseCase


class RotateApiKeyUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
        api_key_adapter: ApiKeyPort,
    ):
        super().__init__(query_repository)
        self.command_repository = command_repository
        self.api_key_adapter = api_key_adapter

    async def execute(
        self, session: SessionType, project_id: UUID, user_id: UUID
    ) -> str:
        project = await self._get_project_or_404(session, project_id, user_id)
        api_key_plaintext = self.api_key_adapter.generate(project.id)
        project.api_key_hash = self.api_key_adapter.hash(api_key_plaintext)
        project.updated_at = datetime.now(timezone.utc)
        await self.command_repository.save(session, project)
        return api_key_plaintext
