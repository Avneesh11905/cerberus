"""
Port: User Query Repository
"""

from typing import Protocol
from uuid import UUID

from src.modules.authentication.domain.entities import UserIdentity


class UserQueryRepositoryPort(Protocol):
    """Interface for querying user records."""

    async def find_by_id(self, user_id: UUID) -> UserIdentity | None:
        """Look up a user by their ID. Returns None if not found."""
        ...

    async def find_by_oauth(
        self,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> UserIdentity | None:
        """Look up a user by their OAuth provider + subject ID within a project."""
        ...

    async def find_by_email(
        self, email: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        """Look up a user by email within a project."""
        ...

    async def find_password_hash(self, user_id: UUID) -> str | None:
        """Look up the local password hash for a given user."""
        ...
