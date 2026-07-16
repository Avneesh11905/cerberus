from typing import Generic, Protocol, Sequence, TypeVar

from src.modules.superadmin.domain.entities import SystemLogEntity
from src.shared.domain.enums import LogLevel

SessionType = TypeVar("SessionType", contravariant=True)


class SystemLogRepositoryPort(Protocol, Generic[SessionType]):
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
