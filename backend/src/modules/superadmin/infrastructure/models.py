
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.modules.projects.infrastructure.models import Project
    from src.modules.auth.infrastructure.models import OAuthAccount, Password

from sqlalchemy import (
    Index,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.models import BaseAccountMixin
from src.modules.auth.domain.user import UserRole


class Tenant(BaseAccountMixin, Base):
    """Dashboard users managing projects."""
    __tablename__ = "tenants"

    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, native_enum=True), server_default=text("'TENANT'"), nullable=False)

    owned_projects: Mapped[list["Project"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="tenant", cascade="all, delete-orphan", lazy="selectin")
    password: Mapped[Optional["Password"]] = relationship(back_populates="tenant", cascade="all, delete-orphan", lazy="selectin", uselist=False)

    __table_args__ = (
        Index("uq_tenant_email", "email", unique=True),
        Index("idx_active_tenants", "is_active", postgresql_where=text("deleted_at IS NULL AND is_active = true")),
    )