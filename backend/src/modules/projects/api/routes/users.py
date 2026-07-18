from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.api.dependencies.security import require_role
from src.modules.auth.domain.entities import UserIdentity
from src.modules.projects.api.dependencies import (
    ListProjectUsersUseCaseDep,
    UpdateUserRoleUseCaseDep,
    ToggleUserStatusUseCaseDep,
    ToggleTenantUserStatusUseCaseDep,
)
from src.modules.projects.api.schemas import (
    PaginatedProjectUsersRes,
    ProjectUserRoleUpdateReq,
    ProjectUserStatusUpdateReq,
)
from src.shared.api.dependencies import UnitOfWorkDeps
from src.shared.domain.enums import UserRole

router = APIRouter()


@router.get("/{project_id}/users", response_model=PaginatedProjectUsersRes)
async def list_project_users(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: ListProjectUsersUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """List paginated users for a specific project."""
    skip = (page - 1) * size
    async with uow:
        users, total = await usecase.execute(
            uow.session, project_id, user.id, skip=skip, limit=size, search=search
        )
    return PaginatedProjectUsersRes(
        items=list(users), total=total, page=page, size=size
    )


@router.put("/{project_id}/users/{user_id}/role", response_model=dict)
async def update_project_user_role(
    project_id: UUID,
    user_id: UUID,
    req: ProjectUserRoleUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateUserRoleUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Update the role of an end-user within a project."""
    async with uow:
        updated_user = await usecase.execute(
            uow.session, project_id, user.id, user_id, UserRole(req.role)
        )
    return {
        "message": "Role updated successfully",
        "user_id": str(updated_user.id),
        "role": updated_user.role,
    }


@router.put("/{project_id}/users/{user_id}/status", response_model=dict)
async def update_project_user_status(
    project_id: UUID,
    user_id: UUID,
    req: ProjectUserStatusUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: ToggleUserStatusUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Toggles is_active for a specific user in a project."""
    async with uow:
        updated_user = await usecase.execute(
            uow.session, project_id, user.id, user_id, req.is_active
        )
    return {
        "message": "Status updated successfully",
        "user_id": str(updated_user.id),
        "is_active": updated_user.is_active,
    }


@router.post("/users/{email}/status", response_model=dict)
async def update_tenant_user_status(
    email: str,
    req: ProjectUserStatusUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: ToggleTenantUserStatusUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role("TENANT"))],
):
    """Toggles is_active for a user across all projects owned by the Tenant."""
    async with uow:
        updated_users = await usecase.execute(
            uow.session, user.id, email, req.is_active
        )
    return {
        "message": "Status updated across tenant projects successfully",
        "updated_projects": [u.project_id for u in updated_users],
    }
