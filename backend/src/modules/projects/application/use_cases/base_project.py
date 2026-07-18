from uuid import UUID

from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.projects.domain.exceptions import (
    ProjectForbiddenError,
    ProjectNotFoundError,
)
from src.modules.projects.domain.entities import ProjectEntity


class BaseProjectUseCase[SessionType]:
    def __init__(self, query_repository: ProjectQueryRepositoryPort, **kwargs):
        self.query_repository = query_repository
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def _get_project_or_404(
        self, session: SessionType, project_id: UUID, user_id: UUID | None = None
    ) -> ProjectEntity:
        project = await self.query_repository.get_by_id(session, project_id)
        if not project:
            raise ProjectNotFoundError("Project not found")

        if user_id is not None and project.tenant_id != user_id:
            raise ProjectForbiddenError("Forbidden")

        return project
