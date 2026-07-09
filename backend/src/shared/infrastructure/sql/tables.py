"""
Defines the global declarative base and centralized SQLAlchemy ORM models.
Stores the schema definitions for Users, Projects, RefreshTokens, and OAuthAccounts.
Centralized here because multiple domains (Auth, Users, Projects, Admin) need to query these underlying tables.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from uuid6 import uuid7

from src.authentication.core.domain.user import UserRole

from .connection import Base


class SQLiteCompatibleJSON(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


JSON_TYPE = SQLiteCompatibleJSON


class Project(Base):
    """Represents a Tenant's application, containing API keys and OAuth config."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    private_key: Mapped[str] = mapped_column(String, nullable=False)
    public_key: Mapped[str] = mapped_column(String, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    oauth_config: Mapped[dict] = mapped_column(
        JSON_TYPE, server_default=text("'{}'"), nullable=False
    )
    allowed_origins: Mapped[list[str]] = mapped_column(
        JSON_TYPE, server_default=text("'[]'"), nullable=False
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

    tenant: Mapped["User"] = relationship(
        back_populates="owned_projects", foreign_keys=[tenant_id]
    )
    end_users: Mapped[list["User"]] = relationship(
        back_populates="project",
        foreign_keys="User.project_id",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_allowed_origins_gin", "allowed_origins", postgresql_using="gin"),
    )


class User(Base):
    __tablename__ = "users"

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

    # Tenancy & Role Control
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=True),
        server_default=text("'USER'"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("projects.id", ondelete="CASCADE", use_alter=True),
        index=True,
        nullable=True,
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

    # Relationships
    owned_projects: Mapped[list["Project"]] = relationship(
        back_populates="tenant",
        foreign_keys=[Project.tenant_id],
        cascade="all, delete-orphan",
    )
    project: Mapped[Optional["Project"]] = relationship(
        back_populates="end_users", foreign_keys=[project_id]
    )
    oauth_accounts: Mapped[list["UserOAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    password: Mapped[Optional["UserPassword"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )

    __table_args__ = (
        Index(
            "uq_tenant_email",
            "email",
            postgresql_where=text("project_id IS NULL"),
            unique=True,
        ),
        Index(
            "uq_project_email",
            "email",
            "project_id",
            postgresql_where=text("project_id IS NOT NULL"),
            unique=True,
        ),
        Index(
            "idx_active_users",
            "is_active",
            postgresql_where=text("deleted_at IS NULL AND is_active = true")
        ),
    )


class UserOAuthAccount(Base):
    """One row per OAuth provider per user — enables multi-provider account linking."""

    __tablename__ = "user_oauth_accounts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String, nullable=False)
    oauth_sub: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index(
            "uq_tenant_provider_oauth_sub",
            "provider",
            "oauth_sub",
            postgresql_where=text("project_id IS NULL"),
            unique=True,
        ),
        Index(
            "uq_project_provider_oauth_sub",
            "provider",
            "oauth_sub",
            "project_id",
            postgresql_where=text("project_id IS NOT NULL"),
            unique=True,
        ),
    )

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class UserPassword(Base):
    """Stores local authentication credentials (hashed passwords)."""

    __tablename__ = "user_passwords"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="password")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
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
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    __table_args__ = (Index("idx_active_sessions", "user_id", "used", "expires_at"),)


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    level: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str] = mapped_column(String)
    file: Mapped[str | None] = mapped_column(String, nullable=True)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
