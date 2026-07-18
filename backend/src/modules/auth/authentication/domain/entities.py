"""
Module: Session
Contains pure domain entities related to tracking user sessions and devices.
"""

from datetime import datetime
from uuid import UUID
from pydantic import AnyHttpUrl, BaseModel, EmailStr
from src.modules.auth.authorization.domain.enums import GlobalRole, ProjectRole


class ActiveSession(BaseModel):
    """Represents an active, unexpired login session for a user."""

    family_id: UUID
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_active: datetime
    is_current: bool
    auth_provider: str


class UserIdentity(BaseModel):
    """Pure domain entity — now powered by Pydantic."""

    id: UUID
    email: EmailStr
    is_verified: bool
    role: GlobalRole | ProjectRole
    project_id: UUID | None = None
    name: str | None = None
    picture: AnyHttpUrl | None = None
    deleted_at: datetime | None = None
    updated_at: datetime | None = None


class OAuthUserInfo(BaseModel):
    """Structured data returned by OAuth providers."""

    provider: str
    sub: str
    email: EmailStr
    name: str | None = None
    picture: AnyHttpUrl | None = None
