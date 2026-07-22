from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.authorization.domain.enums import GlobalRole
from src.shared.domain.value_objects import EmailAddress, HttpsUrl


"""
Module: Session
Contains pure domain entities related to tracking user sessions and devices.
"""


@dataclass(kw_only=True)
class UserIdentity:
    """Pure domain entity — now powered by Pydantic."""

    id: UUID
    email: EmailAddress
    is_verified: bool
    role: GlobalRole | str | None = None
    project_id: UUID | None = None
    name: str | None = None
    picture: HttpsUrl | None = None
    deleted_at: datetime | None = None
    updated_at: datetime | None = None
