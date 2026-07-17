from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectQueryRepositoryPort,
)
from src.modules.projects.domain.exceptions import (
    ProjectForbiddenError,
    ProjectNotFoundError,
)


class BaseProjectUserUseCase[SessionType]:
    def __init__(self, project_query_repository: ProjectQueryRepositoryPort, **kwargs):
        self.project_query_repository = project_query_repository
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def _verify_project_ownership(
        self, session: SessionType, project_id: UUID, tenant_id: UUID
    ) -> None:
        project = await self.project_query_repository.get_by_id(session, project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.tenant_id != tenant_id:
            raise ProjectForbiddenError()
