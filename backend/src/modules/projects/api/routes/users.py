from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.authorization.api.dependencies.roles import require_role
from src.modules.auth.authorization.domain.enums import GlobalRole
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.modules.projects.api.dependencies import (
    ListProjectUsersUseCaseDep,

    SetProjectUserActiveStatusUseCaseDep,
    SetTenantUserActiveStatusUseCaseDep,
    GetUserClaimsUseCaseDep,
    UpdateUserClaimsUseCaseDep,
)
from src.modules.projects.api.schemas import (
    PaginatedProjectUsersRes,

    ProjectUserStatusUpdateReq,
    UserClaimsRes,
    UserClaimsOverrideReq,
)
from src.shared.api.dependencies import UnitOfWorkDeps


router = APIRouter()


@router.get("/{project_id}/users", response_model=PaginatedProjectUsersRes)
async def list_project_users(
    project_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: ListProjectUsersUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
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



@router.put("/{project_id}/users/{user_id}/status", response_model=dict)
async def set_project_user_status(
    project_id: UUID,
    user_id: UUID,
    req: ProjectUserStatusUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: SetProjectUserActiveStatusUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
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
async def set_tenant_user_status(
    email: str,
    req: ProjectUserStatusUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: SetTenantUserActiveStatusUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
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


@router.get("/{project_id}/users/{user_id}/claims", response_model=UserClaimsRes)
async def get_user_claims(
    project_id: UUID,
    user_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: GetUserClaimsUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
):
    """Get custom claims for a specific user in a project."""
    async with uow:
        result = await usecase.execute(uow.session, project_id, user.id, user_id)
    return UserClaimsRes(user_id=user_id, **result)


@router.patch("/{project_id}/users/{user_id}/claims", response_model=UserClaimsRes)
async def update_user_claims(
    project_id: UUID,
    user_id: UUID,
    req: UserClaimsOverrideReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateUserClaimsUseCaseDep,
    user: Annotated[UserIdentity, Depends(require_role(GlobalRole.TENANT))],
):
    """Update custom claims overrides for a specific user in a project."""
    async with uow:
        updated = await usecase.execute(
            uow.session, project_id, user.id, user_id, req.overrides
        )
    return UserClaimsRes(
        user_id=user_id,
        default_claims={},  # In a full response this could be fetched if needed, but per plan returning updated.
        user_overrides=updated.custom_claims,
        effective_claims=updated.custom_claims,
    )
