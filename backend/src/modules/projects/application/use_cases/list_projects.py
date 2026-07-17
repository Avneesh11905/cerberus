from typing import Sequence
from uuid import UUID

from src.modules.projects.application.ports import ProjectQueryRepositoryPort
from src.modules.projects.domain.entities import ProjectEntity
from .base_project import BaseProjectUseCase


class ListProjectsUseCase[SessionType](BaseProjectUseCase[SessionType]):
    def __init__(self, query_repository: ProjectQueryRepositoryPort):
        super().__init__(query_repository)

    async def execute(
        self, session: SessionType, user_id: UUID
    ) -> Sequence[ProjectEntity]:
        return await self.query_repository.get_all_for_tenant(session, user_id)
