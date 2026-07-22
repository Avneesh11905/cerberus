from typing import Sequence

from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.domain.entities import SystemLogEntity


class ListTenantLogsUseCase:
    def __init__(self, uow: SuperAdminUoWPort):
        self.uow = uow

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        level: str | None = None,
    ) -> tuple[Sequence[SystemLogEntity], int]:
        async with self.uow:
            from src.shared.domain.enums import LogLevel

            parsed_level = LogLevel(level) if level else None
            logs = await self.uow.log_repo.get_recent_logs(
                skip=skip, limit=limit, level=parsed_level
            )
            total = await self.uow.log_repo.count_logs(level=parsed_level)
            return logs, total
