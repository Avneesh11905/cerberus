"""
Module: SQL System Log Repository Adapter
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import SystemLog
from src.modules.superadmin.domain.repositories import SystemLogRepositoryPort
from src.modules.superadmin.domain.entities import SystemLogEntity

class SQLSystemLogRepositoryAdapter(SystemLogRepositoryPort[AsyncSession]):
    def _to_entity(self, orm_model: SystemLog) -> SystemLogEntity:
        return SystemLogEntity.model_validate(orm_model)

    async def get_recent_logs(self, session: AsyncSession, limit: int = 100) -> Sequence[SystemLogEntity]:
        result = await session.execute(
            select(SystemLog).order_by(SystemLog.created_at.desc()).limit(limit)
        )
        orm_models = result.scalars().all()
        return [self._to_entity(model) for model in orm_models]
