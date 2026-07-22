from src.modules.projects.application.dtos.project_dtos import GetProjectDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import GetProjectQuery

from .base_project import BaseProjectUseCase


class GetProjectUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, query: GetProjectQuery) -> GetProjectDTO:
        async with self.uow:
            return GetProjectDTO(
                project=await self._get_project_or_404(
                    self.uow, query.project_id, query.user_id
                )
            )
