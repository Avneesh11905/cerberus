from typing import Sequence

from src.modules.superadmin.application.ports import SystemLogRepositoryPort
from src.modules.superadmin.domain.entities import SystemLogEntity


class ListTenantLogsUseCase[SessionType]:
    def __init__(self, log_repository: SystemLogRepositoryPort):
        self.log_repository = log_repository

    async def execute(
        self,
        session: SessionType,
        skip: int = 0,
        limit: int = 100,
        level: str | None = None,
    ) -> tuple[Sequence[SystemLogEntity], int]:
        from src.shared.domain.enums import LogLevel

        parsed_level = LogLevel(level) if level else None
        logs = await self.log_repository.get_recent_logs(
            session, skip=skip, limit=limit, level=parsed_level
        )
        total = await self.log_repository.count_logs(session, level=parsed_level)
        return logs, total
