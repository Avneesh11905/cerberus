from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


"""
Module: Session
Contains pure domain entities related to tracking user sessions and devices.
"""


@dataclass(kw_only=True)
class ActiveSession:
    """Represents an active, unexpired login session for a user."""

    family_id: UUID
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_active: datetime
    is_current: bool
    auth_provider: str
