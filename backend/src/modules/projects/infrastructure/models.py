from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.modules.superadmin.infrastructure.models import Tenant
    from src.modules.users.infrastructure.models import User

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from src.core.database import Base


class Project(Base):
    """Represents a Tenant's application, containing API keys and OAuth config."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    admin_email: Mapped[str | None] = mapped_column(String, nullable=True)
    private_key: Mapped[str] = mapped_column(String, nullable=False)
    public_key: Mapped[str] = mapped_column(String, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    oauth_config: Mapped[dict] = mapped_column(
        JSONB, server_default=text("'{}'"), nullable=False
    )
    allowed_origins: Mapped[list[str]] = mapped_column(
        JSONB, server_default=text("'[]'"), nullable=False
    )
    default_claims: Mapped[dict] = mapped_column(
        JSONB, server_default=text("'{}'"), nullable=False
    )
    environment: Mapped[str] = mapped_column(
        String, server_default=text("'development'"), nullable=False
    )
    frontend_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="owned_projects")
    end_users: Mapped[list["User"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_allowed_origins_gin", "allowed_origins", postgresql_using="gin"),
    )
