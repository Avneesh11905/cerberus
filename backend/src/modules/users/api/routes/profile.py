"""
Exposes HTTP endpoints for managing user profiles.
Handles fetching, updating, and completely deleting a user's account.
During deletion, it ensures the current session is securely terminated by blacklisting the active JWT.
"""

from fastapi import APIRouter, Request, Response

from src.modules.auth.authentication.api.dependencies.security import (
    GetCurrentUserDep,
    GetJWTPayloadDep,
    VerifyCSRFDep,
)
from src.modules.users.api.schemas import ProfileUpdate, UserProfileRes
from src.modules.users.api.dependencies import (
    GetProfileUseCaseDep,
    UpdateProfileUseCaseDep,
    DeleteAccountUseCaseDep,
)
from src.shared.api.dependencies import UnitOfWorkDeps
from src.shared.api.utils import delete_refresh_token_cookie

router = APIRouter()


@router.get("/me", response_model=UserProfileRes)
async def get_profile(
    request: Request,
    current_user: GetCurrentUserDep,
    uow: UnitOfWorkDeps,
    use_case: GetProfileUseCaseDep,
):
    """
    Fetch the current user's profile information.

    Requires a valid JWT Access Token. Returns basic profile details like the user's ID, email, display name, and profile picture URL.

    **Returns:**
    The user's profile object.
    """
    async with uow:
        profile = await use_case.execute(uow.session, current_user.id)

    return UserProfileRes.model_validate(profile)


@router.patch("/me", dependencies=[VerifyCSRFDep], response_model=UserProfileRes)
async def update_profile(
    request: Request,
    body: ProfileUpdate,
    current_user: GetCurrentUserDep,
    uow: UnitOfWorkDeps,
    use_case: UpdateProfileUseCaseDep,
):
    """
    Update the current user's profile information.

    Allows the user to modify their display name or profile picture URL. Fields omitted from the payload will remain unchanged.

    **Returns:**
    The updated user profile object.
    """
    async with uow:
        updated = await use_case.execute(
            uow.session,
            current_user.id,
            name=body.name,
            picture=str(body.picture) if body.picture else None,
            receive_updates=body.receive_updates,
        )
    return UserProfileRes.model_validate(updated)


@router.delete("/me", dependencies=[VerifyCSRFDep])
async def delete_me(
    request: Request,
    current_user: GetCurrentUserDep,
    jwt_payload: GetJWTPayloadDep,
    uow: UnitOfWorkDeps,
    use_case: DeleteAccountUseCaseDep,
):
    """
    Permanently delete the current user's account.

    This endpoint initiates a cascading deletion of the user's data:
    1. Deletes the core User record (which cascades to delete OAuth links, passwords, and sessions in the database).
    2. Blacklists the current JWT Access Token in Redis to immediately terminate the active session.
    3. Deletes the `refresh_token` HTTP-Only cookie from the browser.

    **Warning:** This action is irreversible.

    **Returns:**
    A 204 No Content response upon successful deletion.
    """

    jti = jwt_payload.get("jti")
    exp = jwt_payload.get("exp")

    async with uow:
        await use_case.execute(uow.session, current_user.id, jti, exp)

    # Clear the refresh token cookie
    response = Response(status_code=204)
    delete_refresh_token_cookie(response)

    return response
