from uuid import UUID

from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.domain.exceptions import (
    ProjectForbiddenError,
    ProjectNotFoundError,
)


class BaseProjectUserUseCase:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def _verify_project_ownership(
        self, uow: ProjectUoWPort, project_id: UUID, tenant_id: UUID | None = None
    ) -> None:
        project = await uow.project_query_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError()

        if tenant_id is not None and project.tenant_id != tenant_id:
            raise ProjectForbiddenError()
