"""
Adapter: SQL User Maintenance Repository
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.authentication.application.ports import (
    UserMaintenanceRepositoryPort,
)
from src.modules.users.infrastructure.models import User


class SQLUserMaintenanceRepositoryAdapter(UserMaintenanceRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    """Implements user maintenance repository ports using SQLAlchemy."""

    async def cleanup_unverified_users(self, hours_old: int = 24) -> int:
        """Delete all unverified users older than `hours_old` hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_old)
        stmt = delete(User).where(User.is_verified.is_(False), User.created_at < cutoff)
        result = await self._session.execute(stmt)
        return int(result.rowcount)  # type: ignore

    async def cleanup_soft_deleted_users(self, days_old: int = 30) -> int:
        """Permanently delete users who were soft-deleted more than `days_old` days ago."""

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        stmt = delete(User).where(
            User.deleted_at.is_not(None), User.deleted_at < cutoff
        )
        result = await self._session.execute(stmt)
        return int(result.rowcount)  # type: ignore
