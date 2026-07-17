from typing import Sequence
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectQueryRepositoryPort,
    ProjectUserRepositoryPort,
)
from src.modules.users.domain.entities import UserProfile
from .base_project_user import BaseProjectUserUseCase


class ListProjectUsersUseCase[SessionType](BaseProjectUserUseCase[SessionType]):
    def __init__(
        self,
        project_query_repository: ProjectQueryRepositoryPort,
        project_user_repository: ProjectUserRepositoryPort,
    ):
        super().__init__(project_query_repository)
        self.project_user_repository = project_user_repository

    async def execute(
        self,
        session: SessionType,
        project_id: UUID,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[UserProfile], int]:
        await self._verify_project_ownership(session, project_id, tenant_id)
        users = await self.project_user_repository.list_project_users(
            session, project_id, skip=skip, limit=limit, search=search
        )
        total = await self.project_user_repository.count_project_users(
            session, project_id, search=search
        )
        return users, total
