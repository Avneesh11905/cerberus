"""
Port: User Maintenance Repository
"""

from typing import Protocol


class UserMaintenanceRepositoryPort[SessionType](Protocol):
    """Interface for background tasks and data cleanup related to users."""

    async def cleanup_unverified_users(self, session: SessionType) -> int:
        """Delete unverified users. Returns number of deleted rows."""
        ...

    async def cleanup_soft_deleted_users(
        self, session: SessionType, days_old: int = 30
    ) -> int:
        """Permanently delete soft-deleted users older than the specified days."""
        ...
