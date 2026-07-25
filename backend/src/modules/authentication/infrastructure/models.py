from datetime import datetime, UTC
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from src.core.database import Base

if TYPE_CHECKING:
    from src.modules.superadmin.infrastructure.models import Tenant
    from src.modules.users.infrastructure.models import User


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    tenant_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )

    provider: Mapped[str] = mapped_column(String, nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        CheckConstraint(
            "(tenant_id IS NOT NULL AND user_id IS NULL) OR (tenant_id IS NULL AND user_id IS NOT NULL)",
            name="chk_oauth_account_owner",
        ),
        Index(
            "uq_tenant_provider_oauth_sub",
            "provider",
            "oauth_sub",
            "tenant_id",
            postgresql_where=text("tenant_id IS NOT NULL"),
            unique=True,
        ),
        Index(
            "uq_user_provider_oauth_sub",
            "provider",
            "oauth_sub",
            "user_id",
            postgresql_where=text("user_id IS NOT NULL"),
            unique=True,
        ),
    )

    tenant: Mapped[Tenant | None] = relationship(back_populates="oauth_accounts")
    user: Mapped[User | None] = relationship(back_populates="oauth_accounts")


class Password(Base):
    __tablename__ = "passwords"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    tenant_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )

    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        CheckConstraint(
            "(tenant_id IS NOT NULL AND user_id IS NULL) OR (tenant_id IS NULL AND user_id IS NOT NULL)",
            name="chk_password_owner",
        ),
        Index(
            "uq_tenant_password",
            "tenant_id",
            postgresql_where=text("tenant_id IS NOT NULL"),
            unique=True,
        ),
        Index(
            "uq_user_password",
            "user_id",
            postgresql_where=text("user_id IS NOT NULL"),
            unique=True,
        ),
    )

    tenant: Mapped[Tenant | None] = relationship(back_populates="password")
    user: Mapped[User | None] = relationship(back_populates="password")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)

    tenant_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True
    )

    family_id: Mapped[UUID] = mapped_column(Uuid, default=uuid7, index=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    auth_provider: Mapped[str] = mapped_column(
        String, nullable=False, server_default="local"
    )

    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "(tenant_id IS NOT NULL AND user_id IS NULL) OR (tenant_id IS NULL AND user_id IS NOT NULL)",
            name="chk_refresh_token_owner",
        ),
    )
