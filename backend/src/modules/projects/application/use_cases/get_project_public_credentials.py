from src.modules.projects.application.dtos.project_dtos import (
    GetProjectPublicCredentialsDTO,
)
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.queries.project_queries import (
    GetProjectPublicCredentialsQuery,
)

from .base_project import BaseProjectUseCase


class GetProjectPublicCredentialsUseCase(BaseProjectUseCase):
    def __init__(self, uow: ProjectUoWPort):
        self.uow = uow
        super().__init__()

    async def execute(
        self, query: GetProjectPublicCredentialsQuery
    ) -> GetProjectPublicCredentialsDTO:
        async with self.uow:
            project = await self._get_project_or_404(
                self.uow, query.project_id, query.user_id
            )
            return GetProjectPublicCredentialsDTO(
                public_key=project.public_key, api_key_hash=project.api_key_hash
            )
