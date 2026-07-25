from dataclasses import dataclass
from uuid import UUID

from src.modules.users.domain.entities.user_profile import UserProfile


@dataclass(kw_only=True)
class ProjectUser(UserProfile):
    project_id: UUID
