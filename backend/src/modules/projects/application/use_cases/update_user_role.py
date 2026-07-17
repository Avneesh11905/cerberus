from uuid import UUID

from src.modules.projects.application.ports import (
    ProjectQueryRepositoryPort,
    ProjectUserRepositoryPort,
)
from src.modules.projects.domain.exceptions import ProjectError, ProjectNotFoundError
from src.modules.users.domain.entities import UserProfile
from src.shared.domain.enums import UserRole
from .base_project_user import BaseProjectUserUseCase


class UpdateUserRoleUseCase[SessionType](BaseProjectUserUseCase[SessionType]):
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
        user_id: UUID,
        new_role: UserRole,
    ) -> UserProfile:
        if new_role not in (UserRole.ADMIN, UserRole.USER):
            raise ProjectError()
        await self._verify_project_ownership(session, project_id, tenant_id)
        user = await self.project_user_repository.update_user_role(
            session, project_id, user_id, new_role
        )
        if not user:
            raise ProjectNotFoundError()
        return user
