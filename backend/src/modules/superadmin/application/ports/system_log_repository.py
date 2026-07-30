from typing import Protocol
from collections.abc import Sequence
from datetime import datetime

from src.modules.superadmin.domain.entities import SystemLogEntity
from src.shared.domain.enums import LogLevel


class SystemLogRepositoryPort(Protocol):
    async def get_recent_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        level: LogLevel | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Sequence[SystemLogEntity]: ...

    async def count_logs(
        self, 
        level: LogLevel | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int: ...
