from typing import Annotated

from fastapi import Depends, HTTPException

from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.presentation.api.dependencies.security import (
    GetCurrentUserDep,
)
from src.modules.authorization.domain.enums import GlobalRole


def require_role(required_role: GlobalRole):
    """
    Dependency generator that checks if the authenticated user has the required role.
    SUPERADMIN has unrestricted access globally. ADMIN has unrestricted access within their tenant.
    """

    def role_checker(user: GetCurrentUserDep) -> UserIdentity:
        if user.role == GlobalRole.SUPERADMIN:
            return user
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user

    return role_checker


RequireTenantRoleDep = Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))]
RequireSuperAdminRoleDep = Annotated[
    UserIdentity, Depends(require_role(GlobalRole.SUPERADMIN))
]
