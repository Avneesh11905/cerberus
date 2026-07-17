"""
Port: User Query Repository
"""

from typing import Protocol
from uuid import UUID

from src.modules.auth.domain.entities import UserIdentity


class UserQueryRepositoryPort[SessionType](Protocol):
    """Interface for querying user records."""

    async def find_by_id(
        self, session: SessionType, user_id: UUID
    ) -> UserIdentity | None:
        """Look up a user by their ID. Returns None if not found."""
        ...

    async def find_by_oauth(
        self,
        session: SessionType,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> UserIdentity | None:
        """Look up a user by their OAuth provider + subject ID within a project."""
        ...

    async def find_by_email(
        self, session: SessionType, email: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        """Look up a user by email within a project."""
        ...

    async def find_password_hash(
        self, session: SessionType, user_id: UUID
    ) -> str | None:
        """Look up the local password hash for a given user."""
        ...

    async def is_project_admin(
        self, session: SessionType, project_id: UUID, email: str
    ) -> bool:
        """Check if an email matches the project's admin_email."""
        ...
