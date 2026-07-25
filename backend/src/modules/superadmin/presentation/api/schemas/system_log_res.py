from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.shared.domain.enums import LogLevel


class SystemLogRes(BaseModel):
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: str | None
    line: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
