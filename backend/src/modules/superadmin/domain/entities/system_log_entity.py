from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.shared.domain.enums import LogLevel


@dataclass(kw_only=True)
class SystemLogEntity:
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: str | None
    line: int | None
    created_at: datetime
