"""
Exposes HTTP endpoints for the password reset flow (both requesting a reset and executing it).
Translates HTTP requests into the corresponding `PasswordResetRequestUseCase` and `PasswordResetExecuteUseCase`.
"""

from fastapi import APIRouter, HTTPException, Request

from src.modules.auth.authentication.api.dependencies.use_cases import (
    PasswordChangeUseCaseDep,
    PasswordResetExecuteUseCaseDep,
    PasswordResetRequestUseCaseDep,
)
from src.modules.auth.authentication.api.dependencies.security import (
    GetCurrentUserDep,
    VerifyCSRFDep,
)
from src.modules.auth.authentication.api.dependencies.project import (
    OptionalProjectIdDep,
)
from src.modules.auth.authentication.api.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.shared.api.dependencies import UnitOfWorkDeps, IsChallengedDep
from src.shared.api.utils import extract_client_metadata

router = APIRouter(prefix="/password")


@router.post("/forgot", response_model=MessageResponse)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    uow: UnitOfWorkDeps,
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
    async with uow:
        await usecase.execute(
            uow,
            body.email,
            project_id=project_id,
            is_challenged=is_challenged,
            turnstile_token=body.turnstile_token,
            client_meta=client_meta,
        )

    # We always return 200 OK to prevent email enumeration
    return MessageResponse(
        message="If an account with that email exists, we sent a password reset link."
    )


@router.post("/reset", response_model=MessageResponse)
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    uow: UnitOfWorkDeps,
    usecase: PasswordResetExecuteUseCaseDep,
    is_challenged: IsChallengedDep,
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
    async with uow:
        success = await usecase.execute(
            uow,
            body.token,
            body.new_password,
            is_challenged=is_challenged,
            turnstile_token=body.turnstile_token,
            client_meta=client_meta,
        )
        if not success:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
    return MessageResponse(message="Password successfully reset")


@router.patch("/", response_model=MessageResponse, dependencies=[VerifyCSRFDep])
async def change_password(
    request: Request,
    req: ChangePasswordRequest,
    current_user: GetCurrentUserDep,
    uow: UnitOfWorkDeps,
    usecase: PasswordChangeUseCaseDep,
):
    """
    Update the authenticated user's or tenant's password.
    """
    async with uow:
        await usecase.execute(
            uow, current_user.id, req.current_password, req.new_password
        )
    return MessageResponse(message="Password updated successfully")
