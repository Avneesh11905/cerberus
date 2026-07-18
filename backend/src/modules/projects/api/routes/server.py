from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.authentication.api.dependencies.project import (
    get_required_project_id,
)
from src.modules.projects.api.dependencies import (
    ListProjectUsersUseCaseDep,
    SetProjectUserActiveStatusUseCaseDep,
    GetUserClaimsUseCaseDep,
    UpdateUserClaimsUseCaseDep,
)
from src.modules.projects.api.schemas import (
    PaginatedProjectUsersRes,
    ProjectUserStatusUpdateReq,
    UserClaimsOverrideReq,
    UserClaimsRes,
)
from src.shared.api.dependencies import UnitOfWorkDeps


router = APIRouter(prefix="/server", tags=["Server M2M"])


@router.get("/users", response_model=PaginatedProjectUsersRes)
async def list_project_users_m2m(
    uow: UnitOfWorkDeps,
    usecase: ListProjectUsersUseCaseDep,
    project_id: Annotated[UUID, Depends(get_required_project_id)],
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """
    List paginated users for the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    skip = (page - 1) * size
    async with uow:
        users, total = await usecase.execute(
            uow.session, project_id, None, skip=skip, limit=size, search=search
        )
    return PaginatedProjectUsersRes(
        items=list(users), total=total, page=page, size=size
    )


@router.put("/users/{user_id}/status", response_model=dict)
async def set_project_user_status_m2m(
    user_id: UUID,
    req: ProjectUserStatusUpdateReq,
    uow: UnitOfWorkDeps,
    usecase: SetProjectUserActiveStatusUseCaseDep,
    project_id: Annotated[UUID, Depends(get_required_project_id)],
):
    """
    Toggles is_active for a specific user in the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    async with uow:
        updated_user = await usecase.execute(
            uow.session, project_id, None, user_id, req.is_active
        )
    return {
        "message": "Status updated successfully",
        "user_id": str(updated_user.id),
        "is_active": updated_user.is_active,
    }


@router.get("/users/{user_id}/claims", response_model=UserClaimsRes)
async def get_user_claims_m2m(
    user_id: UUID,
    uow: UnitOfWorkDeps,
    usecase: GetUserClaimsUseCaseDep,
    project_id: Annotated[UUID, Depends(get_required_project_id)],
):
    """
    Get custom claims for a specific user in the project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    async with uow:
        result = await usecase.execute(uow.session, project_id, None, user_id)
    return UserClaimsRes(user_id=user_id, **result)


@router.patch("/users/{user_id}/claims", response_model=UserClaimsRes)
async def update_user_claims_m2m(
    user_id: UUID,
    req: UserClaimsOverrideReq,
    uow: UnitOfWorkDeps,
    usecase: UpdateUserClaimsUseCaseDep,
    project_id: Annotated[UUID, Depends(get_required_project_id)],
):
    """
    Update custom claims for a specific user in a project.
    Intended for Server-to-Server (M2M) operations using the Project API Key (X-Cerberus-API-Key).
    """
    async with uow:
        # Pass tenant_id=None because we rely on the Project API Key for authorization
        updated = await usecase.execute(
            uow.session, project_id, None, user_id, req.overrides
        )
    return UserClaimsRes(
        user_id=user_id,
        default_claims={},
        user_overrides=updated.custom_claims,
        effective_claims=updated.custom_claims,
    )
