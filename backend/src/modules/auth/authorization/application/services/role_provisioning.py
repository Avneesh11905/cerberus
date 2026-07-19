from uuid import UUID

from src.core.config import core_settings
from src.modules.auth.authorization.domain.enums import GlobalRole


class RoleProvisioningService[SessionType]:
    """
    Service responsible for determining the correct default role for a user upon registration.
    This encapsulates the authorization business rules (like superadmin checks and project owner checks)
    so they don't leak into the authentication flows.
    """

    async def determine_default_role(
        self, session: SessionType, email: str, project_id: UUID | None = None
    ) -> GlobalRole | None:
        """
        Determine the role for a new user based on context and email.
        """
        if project_id is not None:
            return None
        else:
            if (
                core_settings.SUPERADMIN_EMAIL
                and email.strip().lower()
                == core_settings.SUPERADMIN_EMAIL.strip().lower()
            ):
                return GlobalRole.SUPERADMIN
            return GlobalRole.TENANT
