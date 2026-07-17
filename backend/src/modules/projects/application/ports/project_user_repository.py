"""
Defines the interface (Port) for interacting with end-users belonging to a specific project.
Allows project owners (tenants) to manage the users of their projects.
"""

from typing import Protocol, Sequence
from uuid import UUID

from src.modules.users.domain.entities import UserProfile
from src.shared.domain.enums import UserRole


class ProjectUserRepositoryPort[SessionType](Protocol):
    async def list_project_users(
        self,
        session: SessionType,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[UserProfile]:
        """Fetch a paginated list of users for a specific project."""
        ...

    async def count_project_users(
        self, session: SessionType, project_id: UUID, search: str | None = None
    ) -> int:
        """Count the total number of users for a specific project matching the search."""
        ...

    async def update_user_role(
        self, session: SessionType, project_id: UUID, user_id: UUID, new_role: UserRole
    ) -> UserProfile | None:
        """Update the role of a user within a project."""
        ...

    async def update_user_status(
        self, session: SessionType, project_id: UUID, user_id: UUID, is_active: bool
    ) -> UserProfile | None:
        """Update the active status of a user within a project."""
        ...

    async def update_tenant_user_status(
        self, session: SessionType, tenant_id: UUID, email: str, is_active: bool
    ) -> Sequence[UserProfile]:
        """Update the active status of a user across all projects owned by a tenant."""
        ...
