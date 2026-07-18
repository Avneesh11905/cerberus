from typing import Protocol
from uuid import UUID

from src.core.config import core_settings
from src.modules.auth.authorization.domain.enums import GlobalRole, ProjectRole


class ProjectAdminQueryPort[SessionType](Protocol):
    """Interface to query if a user is an admin of a project."""

    async def is_project_admin(
        self, session: SessionType, project_id: UUID, email: str
    ) -> bool: ...


class RoleProvisioningService[SessionType]:
    """
    Service responsible for determining the correct default role for a user upon registration.
    This encapsulates the authorization business rules (like superadmin checks and project owner checks)
    so they don't leak into the authentication flows.
    """

    def __init__(self, admin_query_repo: ProjectAdminQueryPort[SessionType]):
        self._admin_query_repo = admin_query_repo

    async def determine_default_role(
        self, session: SessionType, email: str, project_id: UUID | None = None
    ) -> GlobalRole | ProjectRole:
        """
        Determine the role for a new user based on context and email.
        """
        if project_id is not None:
            is_admin = await self._admin_query_repo.is_project_admin(
                session, project_id, email
            )
            if is_admin:
                return ProjectRole.ADMIN
            return ProjectRole.USER
        else:
            if (
                core_settings.SUPERADMIN_EMAIL
                and email.strip().lower()
                == core_settings.SUPERADMIN_EMAIL.strip().lower()
            ):
                return GlobalRole.SUPERADMIN
            return GlobalRole.TENANT
