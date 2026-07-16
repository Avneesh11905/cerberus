from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from src.core.database import Base
from src.shared.domain.enums import LogLevel


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    level: Mapped[LogLevel] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str] = mapped_column(String)
    file: Mapped[str | None] = mapped_column(String, nullable=True)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
