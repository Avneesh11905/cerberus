"""
Module: User
"""

from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, EmailStr

from src.shared.domain.enums import UserRole


class UserIdentity(BaseModel):
    """Pure domain entity — now powered by Pydantic."""

    id: UUID
    email: EmailStr
    is_verified: bool
    role: UserRole
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
