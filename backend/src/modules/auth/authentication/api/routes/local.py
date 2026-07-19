from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from src.modules.auth.authentication.api.dependencies.project import (
    get_optional_project_id,
)
from src.modules.auth.authentication.api.dependencies.use_cases import (
    get_local_login_usecase,
    get_local_register_usecase,
)
from src.modules.auth.authentication.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from src.modules.auth.authentication.application.use_cases import (
    LocalLoginUseCase,
    LocalRegisterUseCase,
)
from src.shared.api.dependencies import UnitOfWorkDeps, get_is_challenged
from src.shared.api.utils import (
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
)

router = APIRouter()

"""
Exposes HTTP endpoints for local email/password registration and login.
Separates User (SDK) and Tenant (Dashboard) authentication.
"""

# ---------------------------------------------------------
# User Authentication (Requires Project API Key)
# ---------------------------------------------------------


@router.post("/register", status_code=201, response_model=RegisterResponse)
async def register_user(
    request: Request,
    req: RegisterRequest,
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalRegisterUseCase, Depends(get_local_register_usecase)],
    is_challenged: Annotated[bool, Depends(get_is_challenged)],
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
):
    """
    Register a new end-user for a specific project.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        expires_in = await usecase.execute(
            uow,
            req.email,
            req.password,
            req.name,
            project_id=project_id,
            client_meta=client_meta,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )
    return RegisterResponse(
        message="Successfully registered! Please check your email for the 6-digit OTP code.",
        expires_in_seconds=expires_in,
    )


# ---------------------------------------------------------
# User Authentication (Requires Project API Key)
# ---------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: Request,
    req: LoginRequest,
    response: Response,
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalLoginUseCase, Depends(get_local_login_usecase)],
    is_challenged: Annotated[bool, Depends(get_is_challenged)],
    project_id: Annotated[UUID, Depends(get_optional_project_id)],
):
    """
    Authenticate an end-user.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        profile, refresh_token, access_token = await usecase.execute(
            uow,
            req.email,
            req.password,
            client_meta=client_meta,
            project_id=project_id,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )

    set_refresh_token_cookie(response, refresh_token)
    csrf_token = generate_csrf_token(refresh_token)

    return LoginResponse(
        message="Authenticated successfully",
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump() if profile else {},
    )
