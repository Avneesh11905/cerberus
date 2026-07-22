from src.modules.projects.application.dtos.project_dtos import ListProjectUsersDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import (
    ListProjectUsersQuery,
)

from .base_project_user import BaseProjectUserUseCase


class ListProjectUsersUseCase(BaseProjectUserUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(self, query: ListProjectUsersQuery) -> ListProjectUsersDTO:
        async with self.uow:
            await self._verify_project_ownership(
                self.uow, query.project_id, query.tenant_id
            )
            users = await self.uow.project_user_repo.list_project_users(
                query.project_id,
                skip=query.skip,
                limit=query.limit,
                search=query.search,
            )
            total = await self.uow.project_user_repo.count_project_users(
                query.project_id, search=query.search
            )
            return ListProjectUsersDTO(users=users, total=total)
