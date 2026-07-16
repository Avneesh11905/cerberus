"""
Module: Project User Management Use Cases
"""

from typing import Any, Sequence
from uuid import UUID

from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.modules.projects.application.ports.project_user_repository import (
    ProjectUserRepositoryPort,
)
from src.modules.projects.domain.exceptions import (
    ProjectError,
    ProjectForbiddenError,
    ProjectNotFoundError,
)
from src.modules.users.domain import UserProfile
from src.shared.domain.enums import UserRole


class ProjectUserManagementUseCase:
    """Coordinates business logic for managing users within a project."""

    def __init__(
        self,
        project_query_repository: ProjectQueryRepositoryPort,
        project_user_repository: ProjectUserRepositoryPort,
    ):
        self.project_query_repository = project_query_repository
        self.project_user_repository = project_user_repository

    async def _verify_project_ownership(
        self, session: Any, project_id: UUID, tenant_id: UUID
    ) -> None:
        """Ensure the tenant owns the project."""
        project = await self.project_query_repository.get_by_id(session, project_id)
        if not project:
            raise ProjectNotFoundError()

        if project.tenant_id != tenant_id:
            raise ProjectForbiddenError()

    async def list_project_users(
        self,
        session: Any,
        project_id: UUID,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[UserProfile], int]:
        """Fetch a paginated list of users for a project, verifying ownership first."""
        await self._verify_project_ownership(session, project_id, tenant_id)

        users = await self.project_user_repository.list_project_users(
            session, project_id, skip=skip, limit=limit, search=search
        )
        total = await self.project_user_repository.count_project_users(
            session, project_id, search=search
        )
        return users, total

    async def update_user_role(
        self,
        session: Any,
        project_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        new_role: UserRole,
    ) -> UserProfile:
        """Update the role of a user within a project, verifying ownership first."""
        if new_role not in (UserRole.ADMIN, UserRole.USER):
            raise ProjectError()

        await self._verify_project_ownership(session, project_id, tenant_id)

        user = await self.project_user_repository.update_user_role(
            session, project_id, user_id, new_role
        )
        if not user:
            raise ProjectNotFoundError()

        return user

    async def toggle_user_status(
        self,
        session: Any,
        project_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        is_active: bool,
    ) -> UserProfile:
        """Update the active status of a user within a project."""
        await self._verify_project_ownership(session, project_id, tenant_id)

        user = await self.project_user_repository.update_user_status(
            session, project_id, user_id, is_active
        )
        if not user:
            raise ProjectNotFoundError()

        return user

    async def toggle_tenant_user_status(
        self,
        session: Any,
        tenant_id: UUID,
        email: str,
        is_active: bool,
    ) -> Sequence[UserProfile]:
        """Update the active status of a user across all projects owned by a tenant."""
        # tenant_id verifies ownership implicitly through the repository query joining Projects
        users = await self.project_user_repository.update_tenant_user_status(
            session, tenant_id, email, is_active
        )
        if not users:
            raise ProjectNotFoundError()

        return users
