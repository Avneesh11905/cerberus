"""
Defines the interface (Port) for interacting with end-users belonging to a specific project.
Allows project owners (tenants) to manage the users of their projects.
"""

from typing import Protocol
from collections.abc import Sequence, Mapping
from uuid import UUID
from pydantic import JsonValue

from src.modules.projects.domain.entities.project_user import ProjectUser


class ProjectUserRepositoryPort(Protocol):
    async def list_project_users(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[ProjectUser], int]:
        """Fetch a paginated list of users for a specific project and the total count."""
        ...

    async def list_tenant_users(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[ProjectUser], int]:
        """Fetch a paginated list of users across all projects for a specific tenant and the total count."""
        ...

    async def update_user_status(
        self, project_id: UUID, user_id: UUID, is_active: bool
    ) -> ProjectUser | None:
        """Update the active status of a user within a project."""
        ...

    async def update_tenant_user_status(
        self, tenant_id: UUID, email: str, is_active: bool
    ) -> Sequence[ProjectUser]:
        """Update the active status of a user across all projects owned by a tenant."""
        ...

    async def update_user_claims(
        self, project_id: UUID, user_id: UUID, overrides: Mapping[str, JsonValue]
    ) -> ProjectUser | None:
        """Update custom claims for a user in a project."""
        ...
