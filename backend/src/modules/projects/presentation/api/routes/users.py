from uuid import UUID
from src.modules.users.presentation.api.schemas.user_profile_res import UserProfileRes

from fastapi import APIRouter

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireTenantRoleDep,
)
from src.modules.projects.application.commands.project_commands import (
    SetProjectUserActiveStatusCommand,
    SetTenantUserActiveStatusCommand,
    UpdateUserClaimsCommand,
)
from src.modules.projects.application.queries.project_queries import (
    GetUserClaimsQuery,
    ListProjectUsersQuery,
)
from src.modules.projects.presentation.api.schemas import (
    PaginatedProjectUsersRes,
    ProjectUserStatusUpdateReq,
    ProjectUserStatusUpdateRes,
    UserClaimsOverrideReq,
    UserClaimsRes,
)
from src.modules.projects.wiring import (
    GetUserClaimsUseCaseDep,
    ListProjectUsersUseCaseDep,
    SetProjectUserActiveStatusUseCaseDep,
    SetTenantUserActiveStatusUseCaseDep,
    UpdateUserClaimsUseCaseDep,
)

router = APIRouter()


@router.get("/{project_id}/users", response_model=PaginatedProjectUsersRes)
async def list_project_users(
    project_id: UUID,
    usecase: ListProjectUsersUseCaseDep,
    user: RequireTenantRoleDep,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """List paginated users for a specific project."""
    skip = (page - 1) * size
    dto = await usecase.execute(
        ListProjectUsersQuery(
            project_id=project_id,
            tenant_id=user.id,
            skip=skip,
            limit=size,
            search=search,
        ),
    )
    users = dto.users
    total = dto.total
    return PaginatedProjectUsersRes(
        items=[UserProfileRes.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
    )


@router.put(
    "/{project_id}/users/{user_id}/status", response_model=ProjectUserStatusUpdateRes
)
async def set_project_user_status(
    project_id: UUID,
    user_id: UUID,
    req: ProjectUserStatusUpdateReq,
    usecase: SetProjectUserActiveStatusUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Toggles is_active for a specific user in a project."""
    dto = await usecase.execute(
        SetProjectUserActiveStatusCommand(
            project_id=project_id,
            tenant_id=user.id,
            user_id=user_id,
            is_active=req.is_active,
        ),
    )
    updated_user = dto.user
    return ProjectUserStatusUpdateRes(
        message="Status updated successfully",
        user_id=updated_user.id,
        is_active=updated_user.is_active,
    )


@router.post("/users/{email}/status", response_model=dict)
async def set_tenant_user_status(
    email: str,
    req: ProjectUserStatusUpdateReq,
    usecase: SetTenantUserActiveStatusUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Toggles is_active for a user across all projects owned by the Tenant."""
    dto = await usecase.execute(
        SetTenantUserActiveStatusCommand(
            tenant_id=user.id, email=email, is_active=req.is_active
        ),
    )
    updated_users = dto.users
    return {
        "message": "Status updated across tenant projects successfully",
        "updated_projects": [u.project_id for u in updated_users],
    }


@router.get("/{project_id}/users/{user_id}/claims", response_model=UserClaimsRes)
async def get_user_claims(
    project_id: UUID,
    user_id: UUID,
    usecase: GetUserClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Get custom claims for a specific user in a project."""
    dto = await usecase.execute(
        GetUserClaimsQuery(project_id=project_id, tenant_id=user.id, user_id=user_id),
    )
    return UserClaimsRes.model_validate({"user_id": user_id, **dto.claims})


@router.patch("/{project_id}/users/{user_id}/claims", response_model=UserClaimsRes)
async def update_user_claims(
    project_id: UUID,
    user_id: UUID,
    req: UserClaimsOverrideReq,
    usecase: UpdateUserClaimsUseCaseDep,
    user: RequireTenantRoleDep,
):
    """Update custom claims overrides for a specific user in a project."""
    dto = await usecase.execute(
        UpdateUserClaimsCommand(
            project_id=project_id,
            tenant_id=user.id,
            user_id=user_id,
            overrides=req.overrides,
        ),
    )
    updated_claims = dto.user.custom_claims
    return UserClaimsRes(
        user_id=user_id,
        default_claims=updated_claims.get("default_claims", {}),
        user_overrides=updated_claims.get("user_overrides", {}),
        effective_claims=updated_claims.get("effective_claims", {}),
    )
