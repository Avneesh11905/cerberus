"""
Exposes HTTP endpoints for the password reset flow (both requesting a reset and executing it).
Translates HTTP requests into the corresponding `PasswordResetRequestUseCase` and `PasswordResetExecuteUseCase`.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from src.modules.auth.api.dependencies.use_cases import (
    get_password_change_usecase,
    get_password_reset_execute_usecase,
    get_password_reset_request_usecase,
)
from src.modules.auth.api.dependencies.security import get_current_user, verify_csrf
from src.modules.auth.api.dependencies.project import get_optional_project_id
from src.modules.auth.api.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.modules.auth.application.use_cases import (
    PasswordChangeUseCase,
    PasswordResetExecuteUseCase,
    PasswordResetRequestUseCase,
)
from src.modules.auth.domain.entities import UserIdentity
from src.shared.api.dependencies import get_is_challenged, UnitOfWorkDeps
from src.shared.api.utils import extract_client_metadata

router = APIRouter(prefix="/password")


@router.post("/forgot", response_model=MessageResponse)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    uow: UnitOfWorkDeps,
    usecase: Annotated[
        PasswordResetRequestUseCase, Depends(get_password_reset_request_usecase)
    ],
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
    is_challenged: bool = Depends(get_is_challenged),
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
    usecase: Annotated[
        PasswordResetExecuteUseCase, Depends(get_password_reset_execute_usecase)
    ],
    is_challenged: bool = Depends(get_is_challenged),
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


@router.patch("/", response_model=MessageResponse, dependencies=[Depends(verify_csrf)])
async def change_password(
    request: Request,
    req: ChangePasswordRequest,
    current_user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: UnitOfWorkDeps,
    usecase: Annotated[PasswordChangeUseCase, Depends(get_password_change_usecase)],
):
    """
    Update the authenticated user's or tenant's password.
    """
    async with uow:
        await usecase.execute(
            uow, current_user.id, req.current_password, req.new_password
        )
    return MessageResponse(message="Password updated successfully")
