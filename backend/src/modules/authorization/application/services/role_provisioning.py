from uuid import UUID

from src.core.config import get_settings
from src.modules.authorization.domain.enums import GlobalRole


class RoleProvisioningService:
    """
    Service responsible for determining the correct default role for a user upon registration.
    This encapsulates the authorization business rules (like superadmin checks and project owner checks)
    so they don't leak into the authentication flows.
    """

    async def determine_default_role(
        self, email: str, project_id: UUID | None = None
    ) -> GlobalRole | None:
        """
        Determine the role for a new user based on context and email.
        """
        if project_id is not None:
            return None
        else:
            super_email = get_settings().core.SUPERADMIN_EMAIL
            if super_email and email.strip().lower() == super_email.strip().lower():
                return GlobalRole.SUPERADMIN
            return GlobalRole.TENANT
