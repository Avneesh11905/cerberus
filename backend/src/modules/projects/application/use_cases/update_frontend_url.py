from datetime import datetime, timezone
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectCommandRepositoryPort,
    ProjectQueryRepositoryPort,
)
from src.modules.projects.domain.entities import ProjectEntity
from .base_project import BaseProjectUseCase


class UpdateFrontendUrlUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(
        self,
        query_repository: ProjectQueryRepositoryPort,
        command_repository: ProjectCommandRepositoryPort,
    ):
        super().__init__(query_repository)
        self.command_repository = command_repository

    async def execute(
        self,
        session: SessionType,
        project_id: UUID,
        user_id: UUID,
        frontend_url: str | None,
    ) -> ProjectEntity:
        project = await self._get_project_or_404(session, project_id, user_id)
        project.frontend_url = frontend_url
        project.updated_at = datetime.now(timezone.utc)
        return await self.command_repository.save(session, project)
