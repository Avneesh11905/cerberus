from fastapi import Depends, HTTPException
from src.modules.auth.authentication.api.dependencies.security import get_current_user
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.modules.auth.authorization.domain.enums import GlobalRole, ProjectRole


def require_role(required_role: GlobalRole | ProjectRole):
    """
    Dependency generator that checks if the authenticated user has the required role.
    SUPERADMIN has unrestricted access globally. ADMIN has unrestricted access within their tenant.
    """

    def role_checker(user: UserIdentity = Depends(get_current_user)):
        if user.role == GlobalRole.SUPERADMIN:
            return user
        if user.role != required_role and user.role != ProjectRole.ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user

    return role_checker
