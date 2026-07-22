from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.shared.domain.enums import LogLevel


class SystemLogRes(BaseModel):
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
