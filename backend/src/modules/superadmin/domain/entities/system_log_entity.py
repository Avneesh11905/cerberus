from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.shared.domain.enums import LogLevel


@dataclass(kw_only=True)
class SystemLogEntity:
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime
