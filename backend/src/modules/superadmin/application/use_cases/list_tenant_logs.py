from collections.abc import Sequence
from datetime import datetime

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
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[Sequence[SystemLogEntity], int]:
        async with self.uow:
            from src.shared.domain.enums import LogLevel

            parsed_level = LogLevel(level) if level else None
            logs = await self.uow.log_repo.get_recent_logs(
                skip=skip,
                limit=limit,
                level=parsed_level,
                start_date=start_date,
                end_date=end_date,
            )
            total = await self.uow.log_repo.count_logs(
                level=parsed_level, start_date=start_date, end_date=end_date
            )
            return logs, total
