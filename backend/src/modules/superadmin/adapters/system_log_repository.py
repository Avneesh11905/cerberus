"""
Module: SQL System Log Repository Adapter
"""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import SystemLog
from src.modules.superadmin.domain.entities import SystemLogEntity
from src.shared.domain.enums import LogLevel


from src.modules.superadmin.application.ports import (
    SystemLogRepositoryPort,
)


class SQLSystemLogRepositoryAdapter(SystemLogRepositoryPort[AsyncSession]):
    def _to_entity(self, orm_model: SystemLog) -> SystemLogEntity:
        return SystemLogEntity.model_validate(orm_model)

    async def get_recent_logs(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        level: LogLevel | None = None,
    ) -> Sequence[SystemLogEntity]:
        stmt = select(SystemLog)
        if level:
            stmt = stmt.where(SystemLog.level == level)

        stmt = stmt.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit)

        result = await session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]

    async def count_logs(
        self, session: AsyncSession, level: LogLevel | None = None
    ) -> int:
        stmt = select(func.count(SystemLog.id))
        if level:
            stmt = stmt.where(SystemLog.level == level)

        result = await session.execute(stmt)
        return result.scalar_one() or 0
