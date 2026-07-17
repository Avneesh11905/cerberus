from uuid import UUID

from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.projects.domain.entities import ProjectEntity
from .base_project import BaseProjectUseCase


class GetProjectUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(self, query_repository: ProjectQueryRepositoryPort):
        super().__init__(query_repository)

    async def execute(
        self, session: SessionType, project_id: UUID, user_id: UUID
    ) -> ProjectEntity:
        return await self._get_project_or_404(session, project_id, user_id)
