from typing import Sequence
from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectQueryRepositoryPort,
    ProjectUserRepositoryPort,
)
from src.modules.projects.domain.exceptions import ProjectNotFoundError
from src.modules.users.domain.entities import UserProfile
from .base_project_user import BaseProjectUserUseCase


class SetTenantUserActiveStatusUseCase[SessionType](
    BaseProjectUserUseCase[SessionType]
):
    def __init__(
        self,
        project_query_repository: ProjectQueryRepositoryPort,
        project_user_repository: ProjectUserRepositoryPort,
    ):
        super().__init__(project_query_repository)
        self.project_user_repository = project_user_repository

    async def execute(
        self, session: SessionType, tenant_id: UUID, email: str, is_active: bool
    ) -> Sequence[UserProfile]:
        users = await self.project_user_repository.update_tenant_user_status(
            session, tenant_id, email, is_active
        )
        if not users:
            raise ProjectNotFoundError()
        return users
