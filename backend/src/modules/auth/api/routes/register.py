from fastapi import APIRouter
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request
from src.modules.auth.api.dependencies.use_cases import get_local_register_usecase
from src.modules.auth.api.dependencies.project import get_required_project_id
from src.modules.auth.api.schemas import (
    RegisterRequest,
    RegisterResponse,
)
from src.modules.auth.application.use_cases import (
    LocalRegisterUseCase,
)
from src.shared.api.dependencies import get_is_challenged, UnitOfWorkDeps
from src.shared.api.utils import (
    extract_client_metadata,
)
from src.shared.domain.enums import UserRole

"""
Exposes HTTP endpoints for local email/password registration.
Separates User (SDK) and Tenant (Dashboard) registration.
"""


router = APIRouter()


# ---------------------------------------------------------
# User Authentication (Requires Project API Key)
# ---------------------------------------------------------


@router.post("/register", status_code=201, response_model=RegisterResponse)
async def register_user(
    request: Request,
    req: RegisterRequest,
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalRegisterUseCase, Depends(get_local_register_usecase)],
    project_id: Annotated[UUID, Depends(get_required_project_id)],
    is_challenged: bool = Depends(get_is_challenged),
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
            role=UserRole.USER,
            client_meta=client_meta,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )
    return RegisterResponse(
        message="Successfully registered! Please check your email for the 6-digit OTP code.",
        expires_in_seconds=expires_in,
    )


# ---------------------------------------------------------
# Tenant Authentication (Dashboard - No Project API Key)
# ---------------------------------------------------------


@router.post("/tenant/register", status_code=201, response_model=RegisterResponse)
async def register_tenant(
    request: Request,
    req: RegisterRequest,
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalRegisterUseCase, Depends(get_local_register_usecase)],
    is_challenged: bool = Depends(get_is_challenged),
):
    """
    Register a new Cerberus tenant dashboard account.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        expires_in = await usecase.execute(
            uow,
            req.email,
            req.password,
            req.name,
            project_id=None,
            role=UserRole.TENANT,
            client_meta=client_meta,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )
    return RegisterResponse(
        message="Successfully registered! Please check your email for the 6-digit OTP code.",
        expires_in_seconds=expires_in,
    )


# ---------------------------------------------------------
# Common Utilities
# ---------------------------------------------------------
