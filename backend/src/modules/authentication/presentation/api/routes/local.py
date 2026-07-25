from fastapi import APIRouter, Request, Response

from src.modules.authentication.application.commands import (
    LocalLoginCommand,
    LocalRegisterCommand,
)
from src.modules.authentication.presentation.api.dependencies.project import (
    OptionalProjectIdDep,
)
from src.modules.authentication.presentation.api.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from src.modules.authentication.presentation.api.utils import (
    generate_csrf_token,
    set_refresh_token_cookie,
)
from src.modules.authentication.wiring import (
    LocalLoginUseCaseDep,
    LocalRegisterUseCaseDep,
)
from src.shared.presentation.api.dependencies import IsChallengedDep
from src.shared.presentation.api.utils import extract_client_metadata

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
    usecase: LocalRegisterUseCaseDep,
    is_challenged: IsChallengedDep,
    project_id: OptionalProjectIdDep,
):
    """
    Register a new end-user for a specific project.
    """
    client_meta = extract_client_metadata(request)
    command = LocalRegisterCommand(
        email=req.email,
        password=req.password,
        name=req.name,
        project_id=project_id,
        client_meta=client_meta,
        is_challenged=is_challenged,
        turnstile_token=req.turnstile_token,
    )
    expires_in = await usecase.execute(command)
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
    usecase: LocalLoginUseCaseDep,
    is_challenged: IsChallengedDep,
    project_id: OptionalProjectIdDep,
):
    """
    Authenticate an end-user.
    """
    client_meta = extract_client_metadata(request)
    command = LocalLoginCommand(
        email=req.email,
        password=req.password,
        client_meta=client_meta,
        project_id=project_id,
        is_challenged=is_challenged,
        turnstile_token=req.turnstile_token,
    )
    profile, refresh_token, access_token = await usecase.execute(command)

    set_refresh_token_cookie(response, refresh_token)
    csrf_token = generate_csrf_token(refresh_token)

    return LoginResponse(
        message="Authenticated successfully",
        csrf_token=csrf_token,
        access_token=access_token,
        user={
            "id": profile.id,
            "email": profile.email.value,
            "name": profile.name,
            "picture": profile.picture.value if profile.picture else None,
            "role": profile.role,
            "is_verified": profile.is_verified,
            "is_active": True,
        }
        if profile
        else None,  # type: ignore
    )
