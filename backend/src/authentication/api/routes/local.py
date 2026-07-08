"""
Exposes HTTP endpoints for local email/password registration.
Parses incoming JSON payloads, validates the data, and triggers the `RegisterLocalUserUseCase`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from uuid import UUID

from src.authentication.api.dependencies import (
    get_current_user,
    verify_csrf,
    get_optional_project_id,
)
from src.authentication.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    LoginResponse,
    RegisterRequest,
)
from src.authentication.api.usecase_dependencies import (
    get_change_password_usecase,
    get_login_local_usecase,
    get_register_local_usecase,
)
from src.authentication.core.domain import UserIdentity, UserRole
from src.authentication.core.usecases import (
    ChangePasswordUseCase,
    LoginLocalUserUseCase,
    RegisterLocalUserUseCase,
)
from src.shared.api.dependencies import limiter
from src.shared.api.utils import (
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
)
from src.shared.config import rate_limit_settings
from src.shared.infrastructure.sql.uow import (
    SQLAlchemyUnitOfWork,
    get_uow,
)  #  was missing, caused NameError at startup
from src.users.container import user_profile_repository

router = APIRouter()


@router.post("/register", status_code=201, response_model=MessageResponse)
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
async def register(
    request: Request,
    req: RegisterRequest,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[RegisterLocalUserUseCase, Depends(get_register_local_usecase)],
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
):
    """
    Register a new user with an email and password.

    This endpoint creates a new unverified user in the system.
    It automatically generates a 6-digit OTP (One Time Password) and sends it to the provided email address via the Resend API.

    The user **cannot login** until they submit the OTP to the `/verify-email` endpoint.

    **Returns:**
    A success message instructing the user to check their email.
    """
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project API key is required for project user registration",
        )

    async with uow:
        await usecase.execute(
            uow,
            req.email,
            req.password,
            req.name,
            project_id=project_id,
            role=UserRole.USER,
        )
    return MessageResponse(
        message="Successfully registered! Please check your email for the 6-digit OTP code."
    )


@router.post("/register/tenant", status_code=201, response_model=MessageResponse)
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
async def register_tenant(
    request: Request,
    req: RegisterRequest,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[RegisterLocalUserUseCase, Depends(get_register_local_usecase)],
):
    """
    Register a new Cerberus tenant dashboard account.

    This route is intentionally separate from project-user registration so role
    assignment is visible at the API boundary.
    """
    async with uow:
        await usecase.execute(
            uow,
            req.email,
            req.password,
            req.name,
            project_id=None,
            role=UserRole.TENANT,
        )
    return MessageResponse(
        message="Successfully registered! Please check your email for the 6-digit OTP code."
    )


@router.post("/login/local", response_model=LoginResponse)
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
async def login_local(
    request: Request,
    req: LoginRequest,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[LoginLocalUserUseCase, Depends(get_login_local_usecase)],
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
):
    """
    Authenticate a user and issue a new session.

    This endpoint verifies the user's email and password. If successful, it establishes a new secure session:

    1. A **Refresh Token** is generated and set as a Secure, HttpOnly cookie.

    **Note:** The user must have verified their email address before they can log in.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        user, refresh_token, access_token = await usecase.execute(
            uow, req.email, req.password, client_meta=client_meta, project_id=project_id
        )
        profile = await user_profile_repository.get_profile(uow.session, user.id)

    set_refresh_token_cookie(response, refresh_token)
    csrf_token = generate_csrf_token(refresh_token)

    return LoginResponse(
        message="Authenticated successfully",
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump(mode="json") if profile else {},
    )


@router.patch(
    "/password", response_model=MessageResponse, dependencies=[Depends(verify_csrf)]
)
@limiter.limit(rate_limit_settings.DEFAULT_RATE_LIMIT)
async def change_password(
    request: Request,
    req: ChangePasswordRequest,
    current_user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[ChangePasswordUseCase, Depends(get_change_password_usecase)],
):
    """
    Update the authenticated user's password.

    If the user already has a password, they must provide the correct `current_password`.
    If they registered via OAuth and never set a password, `current_password` can be omitted.

    **Returns:**
    A success message.
    """
    async with uow:
        await usecase.execute(
            uow, current_user.id, req.current_password, req.new_password
        )
    return MessageResponse(message="Password updated successfully")
