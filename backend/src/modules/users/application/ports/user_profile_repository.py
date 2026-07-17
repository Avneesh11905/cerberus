"""
Defines the interface (Port) for interacting with user profile data.
Abstracts away the underlying database implementation so that business logic can remain pure.
"""

from typing import Any, Protocol
from uuid import UUID

from src.modules.users.domain.entities import UserProfile


class UserProfileRepositoryPort(Protocol):
    async def get_profile(self, session: Any, user_id: UUID) -> UserProfile | None:
        """Fetch the user's profile."""
        ...

    async def save_profile(self, session: Any, profile: UserProfile) -> UserProfile:
        """Save a user's profile."""
        ...

    async def delete_user(self, session: Any, user_id: UUID) -> None:
        """Delete a user and all of their associated data."""
        ...
