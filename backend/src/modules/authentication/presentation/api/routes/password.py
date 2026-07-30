from fastapi import APIRouter, HTTPException, Request

from src.modules.authentication.application.commands import (
    PasswordChangeCommand,
    PasswordResetExecuteCommand,
    PasswordResetRequestCommand,
)
from src.modules.authentication.presentation.api.dependencies.project import (
    OptionalProjectIdDep,
)
from src.modules.authentication.presentation.api.dependencies.security import (
    GetCurrentUserDep,
    VerifyCSRFDep,
)
from src.modules.authentication.presentation.api.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.modules.authentication.wiring import (
    PasswordChangeUseCaseDep,
    PasswordResetExecuteUseCaseDep,
    PasswordResetRequestUseCaseDep,
)
from src.shared.presentation.api.dependencies import IsChallengedDep
from src.shared.presentation.api.utils import extract_client_metadata

"""
Exposes HTTP endpoints for the password reset flow (both requesting a reset and executing it).
Translates HTTP requests into the corresponding `PasswordResetRequestUseCase` and `PasswordResetExecuteUseCase`.
"""

router = APIRouter(prefix="/password")


@router.post("/forgot", response_model=MessageResponse)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    usecase: PasswordResetRequestUseCaseDep,
    project_id: OptionalProjectIdDep,
    is_challenged: IsChallengedDep,
):
    """
    Request a password reset email.

    If the provided email exists in the system, this endpoint generates a secure, single-use reset token and emails a password reset link to the user.

    To prevent email enumeration attacks, this endpoint **always** returns a 200 OK status regardless of whether the email actually exists in the database.
    The heavy lifting is done in a background task so the API responds instantly.

    **Returns:**
    A generic success message.
    """
    client_meta = extract_client_metadata(request)
    command = PasswordResetRequestCommand(
        email=body.email,
        project_id=project_id,
        is_challenged=is_challenged,
        turnstile_token=body.turnstile_token,
        client_meta=client_meta,
    )
    await usecase.execute(command)

    # We always return 200 OK to prevent email enumeration
    return MessageResponse(
        message="If an account with that email exists, we sent a password reset link."
    )


@router.post("/reset", response_model=MessageResponse)
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    usecase: PasswordResetExecuteUseCaseDep,
    is_challenged: IsChallengedDep,
    project_id: OptionalProjectIdDep,
):
    """
    Execute a password reset using a valid token.

    This endpoint accepts the secure reset token (previously sent via email) along with a new password.
    If the token is valid and hasn't expired, the user's password is cryptographically hashed and updated in the database.

    **Returns:**
    A success message upon successful password reset.
    Raises a 400 error if the token is invalid or expired.
    """
    client_meta = extract_client_metadata(request)
    command = PasswordResetExecuteCommand(
        token=body.token,
        new_password=body.new_password,
        project_id=project_id,
        is_challenged=is_challenged,
        turnstile_token=body.turnstile_token,
        client_meta=client_meta,
    )
    success = await usecase.execute(command)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return MessageResponse(message="Password successfully reset")


@router.patch("/", response_model=MessageResponse, dependencies=[VerifyCSRFDep])
async def change_password(
    request: Request,
    req: ChangePasswordRequest,
    current_user: GetCurrentUserDep,
    usecase: PasswordChangeUseCaseDep,
):
    """
    Update the authenticated user's or tenant's password.
    """
    command = PasswordChangeCommand(
        user_id=current_user.id,
        current_password=req.current_password,
        new_password=req.new_password,
    )
    await usecase.execute(command)
    return MessageResponse(message="Password updated successfully")
