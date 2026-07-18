from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.authentication.api.dependencies.project import (
    get_required_project_id,
)
from src.modules.projects.api.dependencies import UpdateUserClaimsUseCaseDep
from src.modules.projects.api.schemas import UserClaimsOverrideReq, UserClaimsRes
from src.shared.api.dependencies import UnitOfWorkDeps


router = APIRouter(prefix="/server", tags=["Server M2M"])


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
