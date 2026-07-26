from src.modules.projects.application.dtos.project_dtos import ListProjectUsersDTO
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import (
    ListTenantUsersQuery,
)


class ListTenantUsersUseCase:
    """
    Fetches paginated end-users across all projects owned by a tenant.
    """

    def __init__(self, uow: ProjectUoWPort):
        self._uow = uow

    async def execute(self, query: ListTenantUsersQuery) -> ListProjectUsersDTO:
        async with self._uow as uow:
            users, total = await uow.project_user_repo.list_tenant_users(
                tenant_id=query.tenant_id,
                skip=query.skip,
                limit=query.limit,
                search=query.search,
            )

            return ListProjectUsersDTO(
                users=list(users),
                total=total,
            )
