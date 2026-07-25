from uuid import UUID
from src.modules.users.presentation.api.schemas.user_profile_res import UserProfileRes

from fastapi import APIRouter

from src.modules.authentication.presentation.api.dependencies.project import (
    RequiredProjectIdDep,
)
from src.modules.projects.application.commands.project_commands import (
    SetProjectUserActiveStatusCommand,
    UpdateUserClaimsCommand,
)
from src.modules.projects.application.queries.project_queries import (
    GetUserClaimsQuery,
    ListProjectUsersQuery,
)
from src.modules.projects.presentation.api.schemas import (
    PaginatedProjectUsersRes,
    ProjectUserStatusUpdateReq,
    UserClaimsOverrideReq,
    UserClaimsRes,
)
from src.modules.projects.wiring import (
    GetUserClaimsUseCaseDep,
    ListProjectUsersUseCaseDep,
    SetProjectUserActiveStatusUseCaseDep,
    UpdateUserClaimsUseCaseDep,
)

router = APIRouter(prefix="/server", tags=["Server M2M"])


@router.get("/users", response_model=PaginatedProjectUsersRes)
async def list_project_users_m2m(
    usecase: ListProjectUsersUseCaseDep,
    project_id: RequiredProjectIdDep,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """
    List paginated users for the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    skip = (page - 1) * size
    dto = await usecase.execute(
        ListProjectUsersQuery(
            project_id=project_id,
            tenant_id=None,
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


@router.put("/users/{user_id}/status", response_model=dict)
async def set_project_user_status_m2m(
    user_id: UUID,
    req: ProjectUserStatusUpdateReq,
    usecase: SetProjectUserActiveStatusUseCaseDep,
    project_id: RequiredProjectIdDep,
):
    """
    Toggles is_active for a specific user in the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    dto = await usecase.execute(
        SetProjectUserActiveStatusCommand(
            project_id=project_id,
            tenant_id=None,
            user_id=user_id,
            is_active=req.is_active,
        ),
    )
    updated_user = dto.user
    return {
        "message": "Status updated successfully",
        "user_id": str(updated_user.id),
        "is_active": updated_user.is_active,
    }


@router.get("/users/{user_id}/claims", response_model=UserClaimsRes)
async def get_user_claims_m2m(
    user_id: UUID,
    usecase: GetUserClaimsUseCaseDep,
    project_id: RequiredProjectIdDep,
):
    """
    Get custom claims for a specific user in the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    dto = await usecase.execute(
        GetUserClaimsQuery(project_id=project_id, tenant_id=None, user_id=user_id),
    )
    claims = dto.claims
    return UserClaimsRes.model_validate({"user_id": user_id, **claims})


@router.patch("/users/{user_id}/claims", response_model=UserClaimsRes)
async def update_user_claims_m2m(
    user_id: UUID,
    req: UserClaimsOverrideReq,
    usecase: UpdateUserClaimsUseCaseDep,
    project_id: RequiredProjectIdDep,
):
    """
    Update custom claims for a specific user in a project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    dto = await usecase.execute(
        UpdateUserClaimsCommand(
            project_id=project_id,
            tenant_id=None,
            user_id=user_id,
            overrides=req.overrides,
        ),
    )
    updated_user = dto.user
    return UserClaimsRes(
        user_id=user_id,
        default_claims={},
        user_overrides=updated_user.custom_claims,
        effective_claims=updated_user.custom_claims,
    )
