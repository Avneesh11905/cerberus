from typing import Protocol, Sequence

from src.modules.superadmin.domain.entities import SystemLogEntity
from src.shared.domain.enums import LogLevel


class SystemLogRepositoryPort[SessionType](Protocol):
    async def get_recent_logs(
        self,
        session: SessionType,
        skip: int = 0,
        limit: int = 100,
        level: LogLevel | None = None,
    ) -> Sequence[SystemLogEntity]: ...

    async def count_logs(
        self, session: SessionType, level: LogLevel | None = None
    ) -> int: ...
