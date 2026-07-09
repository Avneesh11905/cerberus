"""
Exposes HTTP endpoints for the password reset flow (both requesting a reset and executing it).
Translates HTTP requests into the corresponding `RequestPasswordResetUseCase` and `ExecutePasswordResetUseCase`.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select

from src.authentication.api.dependencies import get_optional_project_id
from src.authentication.api.schemas import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
)
from src.authentication.api.usecase_dependencies import (
    get_execute_password_reset_usecase,
    get_request_password_reset_usecase,
)
from src.authentication.core.usecases import (
    ExecutePasswordResetUseCase,
    RequestPasswordResetUseCase,
)
from src.shared.api.dependencies import limiter
from src.shared.config import rate_limit_settings
from src.shared.infrastructure.sql.tables import Project
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter(prefix="/password")


async def _execute_forgot_password_in_background(
    usecase: RequestPasswordResetUseCase,
    email: str,
    project_id: UUID | None = None,
    frontend_url: str | None = None,
) -> None:
    try:
        async with SQLAlchemyUnitOfWork() as uow:
            await usecase.execute(
                uow, email, project_id=project_id, frontend_url=frontend_url
            )
    except Exception as e:
        logging.getLogger(__name__).error(f"Background password reset task failed: {e}")


@router.post("/forgot", response_model=MessageResponse)
@limiter.limit(rate_limit_settings.DEFAULT_RATE_LIMIT)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[
        RequestPasswordResetUseCase, Depends(get_request_password_reset_usecase)
    ],
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
):
    """
    Request a password reset email.

    If the provided email exists in the system, this endpoint generates a secure, single-use reset token and emails a password reset link to the user.

    To prevent email enumeration attacks, this endpoint **always** returns a 200 OK status regardless of whether the email actually exists in the database.
    The heavy lifting is done in a background task so the API responds instantly.

    **Returns:**
    A generic success message.
    """
    frontend_url = None
    if project_id:
        async with uow:
            result = await uow.session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalars().first()
            if project and project.frontend_url:
                frontend_url = project.frontend_url

    background_tasks.add_task(
        _execute_forgot_password_in_background,
        usecase,
        body.email,
        project_id,
        frontend_url,
    )

    # We always return 200 OK to prevent email enumeration
    return MessageResponse(
        message="If an account with that email exists, we sent a password reset link."
    )


@router.post("/reset", response_model=MessageResponse)
@limiter.limit(rate_limit_settings.DEFAULT_RATE_LIMIT)
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[
        ExecutePasswordResetUseCase, Depends(get_execute_password_reset_usecase)
    ],
):
    """
    Execute a password reset using a valid token.

    This endpoint accepts the secure reset token (previously sent via email) along with a new password.
    If the token is valid and hasn't expired, the user's password is cryptographically hashed and updated in the database.

    **Returns:**
    A success message upon successful password reset.
    Raises a 400 error if the token is invalid or expired.
    """
    async with uow:
        success = await usecase.execute(uow, body.token, body.new_password)
        if not success:
            raise HTTPException(
                status_code=400, detail="Invalid or expired reset token"
            )
    return MessageResponse(message="Password successfully reset")
