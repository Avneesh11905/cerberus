from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.modules.auth.authentication.infrastructure.models import (
        OAuthAccount,
        Password,
    )
    from src.modules.projects.infrastructure.models import Project

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from src.core.database import Base
from src.modules.auth.authorization.domain.enums import GlobalRole


class Tenant(Base):
    """Dashboard users managing projects."""

    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    picture: Mapped[str | None] = mapped_column(String, nullable=True)

    is_verified: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    receive_updates: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role: Mapped[GlobalRole] = mapped_column(
        Enum(GlobalRole, native_enum=True),
        server_default=text("'TENANT'"),
        nullable=False,
    )

    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan", lazy="selectin"
    )
    password: Mapped[Optional["Password"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )

    __table_args__ = (
        Index("uq_tenant_email", "email", unique=True),
        Index(
            "idx_active_tenants",
            "is_active",
            postgresql_where=text("deleted_at IS NULL AND is_active = true"),
        ),
    )
