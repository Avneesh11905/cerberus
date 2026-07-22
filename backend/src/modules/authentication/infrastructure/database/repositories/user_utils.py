"""
Shared utilities for mapping SQLAlchemy ORM models to pure Domain Entities.
Ensures that the core Use Cases only ever interact with `UserIdentity` Pydantic models,
preventing SQLAlchemy dependencies from leaking into the business logic layer.
"""

from src.modules.authentication.domain.entities import UserIdentity
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User
from src.shared.domain.value_objects import EmailAddress, HttpsUrl


def to_identity(user: User | Tenant) -> UserIdentity:
    """Map an ORM User or Tenant to a pure domain UserIdentity."""
    return UserIdentity(
        id=user.id,
        email=EmailAddress(user.email),
        is_verified=user.is_verified,
        role=user.role,
        project_id=getattr(user, "project_id", None),
        name=user.name,
        picture=HttpsUrl(str(user.picture)) if user.picture else None,
        deleted_at=user.deleted_at,
        updated_at=user.updated_at,
    )
