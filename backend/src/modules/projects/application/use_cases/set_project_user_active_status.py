from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectQueryRepositoryPort,
    ProjectUserRepositoryPort,
)
from src.modules.projects.domain.exceptions import ProjectNotFoundError
from src.modules.users.domain.entities import UserProfile
from .base_project_user import BaseProjectUserUseCase


class SetProjectUserActiveStatusUseCase[SessionType](
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
        self,
        session: SessionType,
        project_id: UUID,
        tenant_id: UUID | None,
        user_id: UUID,
        is_active: bool,
    ) -> UserProfile:
        await self._verify_project_ownership(session, project_id, tenant_id)
        user = await self.project_user_repository.update_user_status(
            session, project_id, user_id, is_active
        )
        if not user:
            raise ProjectNotFoundError()
        return user
