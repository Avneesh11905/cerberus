"""
Exposes HTTP endpoints for managing user profiles.
Handles fetching, updating, and completely deleting a user's account.
During deletion, it ensures the current session is securely terminated by blacklisting the active JWT.
"""

from fastapi import APIRouter, Request, Response

from src.modules.authentication.presentation.api.dependencies.security import (
    GetCurrentUserDep,
    GetJWTPayloadDep,
    VerifyCSRFDep,
)
from src.modules.authentication.presentation.api.utils import (
    delete_refresh_token_cookie,
)
from src.modules.users.application.commands.user_commands import (
    DeleteAccountCommand,
    UpdateProfileCommand,
)
from src.modules.users.application.queries.user_queries import GetProfileQuery
from src.modules.users.presentation.api.schemas import ProfileUpdate, UserProfileRes
from src.modules.users.wiring import (
    DeleteAccountUseCaseDep,
    GetProfileUseCaseDep,
    UpdateProfileUseCaseDep,
)

router = APIRouter()


@router.get("/me", response_model=UserProfileRes)
async def get_profile(
    request: Request,
    current_user: GetCurrentUserDep,
    use_case: GetProfileUseCaseDep,
):
    """
    Fetch the current user's profile information.

    Requires a valid JWT Access Token. Returns basic profile details like the user's ID, email, display name, and profile picture URL.

    **Returns:**
    The user's profile object.
    """
    query = GetProfileQuery(user_id=current_user.id)
    profile = await use_case.execute(query)

    return UserProfileRes.model_validate(profile)


@router.patch("/me", dependencies=[VerifyCSRFDep], response_model=UserProfileRes)
async def update_profile(
    request: Request,
    body: ProfileUpdate,
    current_user: GetCurrentUserDep,
    use_case: UpdateProfileUseCaseDep,
):
    """
    Update the current user's profile information.

    Allows the user to modify their display name or profile picture URL. Fields omitted from the payload will remain unchanged.

    **Returns:**
    The updated user profile object.
    """
    command = UpdateProfileCommand(
        user_id=current_user.id,
        name=body.name,
        picture=str(body.picture) if body.picture else None,
        receive_updates=body.receive_updates,
    )
    updated = await use_case.execute(command)
    return UserProfileRes.model_validate(updated)


@router.delete("/me", dependencies=[VerifyCSRFDep])
async def delete_me(
    request: Request,
    current_user: GetCurrentUserDep,
    jwt_payload: GetJWTPayloadDep,
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
    command = DeleteAccountCommand(user_id=current_user.id, jwt_jti=jti, jwt_exp=exp)
    await use_case.execute(command)

    # Clear the refresh token cookie
    response = Response(status_code=204)
    delete_refresh_token_cookie(response)

    return response
