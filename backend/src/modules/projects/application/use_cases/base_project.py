from uuid import UUID

from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.domain.entities import ProjectEntity
from src.modules.projects.domain.exceptions import (
    ProjectForbiddenError,
    ProjectNotFoundError,
)


class BaseProjectUseCase:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def _get_project_or_404(
        self, uow: ProjectUoWPort, project_id: UUID, user_id: UUID | None = None
    ) -> ProjectEntity:
        project = await uow.project_query_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError("Project not found")

        if user_id is not None and project.tenant_id != user_id:
            raise ProjectForbiddenError("Forbidden")

        return project
