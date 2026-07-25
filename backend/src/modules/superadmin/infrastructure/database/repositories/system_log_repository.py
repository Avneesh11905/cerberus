"""
Module: SQL System Log Repository Adapter
"""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import SystemLog
from src.modules.superadmin.application.ports import (
    SystemLogRepositoryPort,
)
from src.modules.superadmin.domain.entities import SystemLogEntity
from src.shared.domain.enums import LogLevel


class SQLSystemLogRepositoryAdapter(SystemLogRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, orm_model: SystemLog) -> SystemLogEntity:

        return SystemLogEntity(
            id=orm_model.id,
            level=orm_model.level,
            message=orm_model.message,
            source=orm_model.source,
            created_at=orm_model.created_at,
            file=orm_model.file,
            line=orm_model.line,
        )

    async def get_recent_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        level: LogLevel | None = None,
    ) -> Sequence[SystemLogEntity]:
        stmt = select(SystemLog)
        if level:
            if level == LogLevel.WARN:
                stmt = stmt.where(
                    SystemLog.level.in_([level, "WARNING", "warn", "warning"])
                )
            else:
                stmt = stmt.where(SystemLog.level == level)

        stmt = stmt.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]

    async def count_logs(self, level: LogLevel | None = None) -> int:
        stmt = select(func.count(SystemLog.id))
        if level:
            if level == LogLevel.WARN:
                stmt = stmt.where(
                    SystemLog.level.in_([level, "WARNING", "warn", "warning"])
                )
            else:
                stmt = stmt.where(SystemLog.level == level)

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0
