from src.modules.projects.application.dtos.project_dtos import GetProjectClaimsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import (
    GetProjectClaimsQuery,
)
from src.modules.projects.application.use_cases import BaseProjectUseCase


class GetProjectClaimsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow

    """Retrieves the default custom claims schema for a project."""

    async def execute(self, query: GetProjectClaimsQuery) -> GetProjectClaimsDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, query.project_id, query.user_id
            )
            return GetProjectClaimsDTO(claims=project.default_claims or {})
