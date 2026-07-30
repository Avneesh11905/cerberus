from src.modules.projects.application.dtos.project_dtos import ListProjectsDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import ListProjectsQuery

from .base_project import BaseProjectUseCase


class ListProjectsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, query: ListProjectsQuery) -> ListProjectsDTO:
        async with self.uow:
            projects, total = await self.uow.project_query_repo.get_paginated_for_tenant(
                query.user_id, query.skip, query.limit
            )
            return ListProjectsDTO(projects=projects, total=total)
