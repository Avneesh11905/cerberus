"""
Port: User Command Repository
"""

from typing import Protocol
from uuid import UUID

from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authorization.domain.enums import GlobalRole


class UserCommandRepositoryPort(Protocol):
    """Interface for creating and updating user records."""

    async def create_user_with_oauth(
        self,
        email: str,
        name: str | None,
        picture: str | None,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
        role: GlobalRole | str | None = None,
    ) -> UserIdentity:
        """Create a new user and link an OAuth account."""
        ...

    async def link_oauth_account(
        self,
        user_id: UUID,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> None:
        """Link a new OAuth provider to an existing user."""
        ...

    async def create_user_with_password(
        self,
        email: str,
        name: str | None,
        password_hash: str | None,
        is_verified: bool = False,
        project_id: UUID | None = None,
        role: GlobalRole | str | None = None,
    ) -> UserIdentity:
        """Create a new user and link a local password."""
        ...

    async def update_password(self, user_id: UUID, password_hash: str) -> None:
        """Update or insert a password for a given user ID."""
        ...

    async def disable_local_login(self, user_id: UUID) -> None:
        """Disable local password login for a given user ID."""
        ...

    async def verify_user_email(self, user_id: UUID, name: str | None = None) -> None:
        """Mark a user's email as verified. Updates name if provided."""
        ...

    async def undelete_user(self, user_id: UUID) -> None:
        """Restore a soft-deleted user."""
        ...

    async def update_role(self, user_id: UUID, role: GlobalRole) -> None:
        """Persist a new role for a user. Used for admin self-heal recovery."""
        ...

    async def update_oauth_profile(
        self, user_id: UUID, name: str | None, picture: str | None
    ) -> None:
        """Update a user's name, picture, and mark them verified from OAuth."""
        ...
