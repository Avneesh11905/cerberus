"""
Adapter: SQL User Maintenance Repository
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.application.ports import UserMaintenanceRepositoryPort
from src.modules.users.infrastructure.models import User


class SQLUserMaintenanceRepositoryAdapter(UserMaintenanceRepositoryPort[AsyncSession]):
    """Implements user maintenance repository ports using SQLAlchemy."""

    async def cleanup_unverified_users(
        self, session: AsyncSession, hours_old: int = 24
    ) -> int:
        """Delete all unverified users older than `hours_old` hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_old)
        stmt = delete(User).where(User.is_verified.is_(False), User.created_at < cutoff)
        result = await session.execute(stmt)
        return int(result.rowcount)  # type: ignore

    async def cleanup_soft_deleted_users(
        self, session: AsyncSession, days_old: int = 30
    ) -> int:
        """Permanently delete users who were soft-deleted more than `days_old` days ago."""

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        stmt = delete(User).where(
            User.deleted_at.is_not(None), User.deleted_at < cutoff
        )
        result = await session.execute(stmt)
        return int(result.rowcount)  # type: ignore
