from fastapi import APIRouter
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request, Response
from src.modules.auth.adapters import DBRefreshTokenRepositoryAdapter
from src.modules.auth.api.dependencies import (
    get_current_user,
    get_login_local_usecase,
    get_optional_project_id,
    verify_csrf,
)
from src.modules.auth.api.schemas import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
)
from src.modules.auth.application.use_cases import (
    LoginLocalUserUseCase,
)
from src.modules.auth.domain import UserIdentity
from src.modules.users.adapters import SQLUserProfileRepository
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow
from src.shared.api.dependencies import get_is_challenged
from src.shared.api.utils import (
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
    delete_refresh_token_cookie,
)
from src.modules.auth.application.use_cases.logout_all import LogoutAllUseCase
from src.modules.auth.application.use_cases import LogoutUseCase
from src.modules.auth.api.dependencies import (
    get_jwt_payload,
    get_logout_all_usecase,
    get_logout_usecase,
)
from src.modules.auth.api.dependencies import get_refresh_session_usecase
from src.modules.auth.api.schemas import RefreshResponse
from src.modules.auth.application.use_cases import RefreshSessionUseCase

router = APIRouter()

"""
Exposes HTTP endpoints for local email/password registration and login.
Separates User (SDK) and Tenant (Dashboard) authentication.
"""


# ---------------------------------------------------------
# User Authentication (Requires Project API Key)
# ---------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: Request,
    req: LoginRequest,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[LoginLocalUserUseCase, Depends(get_login_local_usecase)],
    project_id: Annotated[UUID, Depends(get_optional_project_id)],
    is_challenged: bool = Depends(get_is_challenged),
):
    """
    Authenticate an end-user.
    """
    client_meta = extract_client_metadata(request)
    user_repo = SQLUserProfileRepository(
        refresh_repo=DBRefreshTokenRepositoryAdapter(lifetime_days=30)
    )
    async with uow:
        user, refresh_token, access_token = await usecase.execute(
            uow,
            req.email,
            req.password,
            client_meta=client_meta,
            project_id=project_id,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )
        profile = await user_repo.get_profile(uow.session, user.id)

    set_refresh_token_cookie(response, refresh_token)
    csrf_token = generate_csrf_token(refresh_token)

    return LoginResponse(
        message="Authenticated successfully",
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump() if profile else {},
    )


# ---------------------------------------------------------
# Tenant Authentication (Dashboard - No Project API Key)
# ---------------------------------------------------------


@router.post("/tenant/login", response_model=LoginResponse)
async def login_tenant(
    request: Request,
    req: LoginRequest,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[LoginLocalUserUseCase, Depends(get_login_local_usecase)],
    is_challenged: bool = Depends(get_is_challenged),
):
    """
    Authenticate a Cerberus tenant dashboard account.
    """
    client_meta = extract_client_metadata(request)
    user_repo = SQLUserProfileRepository(
        refresh_repo=DBRefreshTokenRepositoryAdapter(lifetime_days=30)
    )
    async with uow:
        user, refresh_token, access_token = await usecase.execute(
            uow,
            req.email,
            req.password,
            client_meta=client_meta,
            project_id=None,
            is_challenged=is_challenged,
            turnstile_token=req.turnstile_token,
        )
        profile = await user_repo.get_profile(uow.session, user.id)

    set_refresh_token_cookie(response, refresh_token)
    csrf_token = generate_csrf_token(refresh_token)

    return LoginResponse(
        message="Authenticated successfully",
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump() if profile else {},
    )


# ---------------------------------------------------------
# Common Utilities
# ---------------------------------------------------------

"""
Exposes HTTP endpoints for refreshing access tokens.
Reads the long-lived refresh token from a secure, HttpOnly cookie,
triggers the `RefreshSessionUseCase`, and returns a fresh short-lived access token.
"""


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: Request,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[RefreshSessionUseCase, Depends(get_refresh_session_usecase)],
):
    """
    Refresh the session and obtain a new Access Token.

    This endpoint reads the HTTP-Only `refresh_token` cookie. It performs **Token Rotation** by invalidating the old refresh token and issuing a brand new one to prevent replay attacks.

    If the refresh token is valid, it returns a fresh 15-minute Access Token in the JSON body, and sets the new Refresh Token in the cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return Response(status_code=204)

    client_meta = extract_client_metadata(request)
    async with uow:
        access_token, new_refresh_token = await usecase.execute(
            uow, refresh_token, client_meta=client_meta
        )

    if not access_token:
        response.status_code = 401
        delete_refresh_token_cookie(response)
        return response

    if new_refresh_token:
        set_refresh_token_cookie(response, new_refresh_token)

    # Derive the CSRF token the same way set_refresh_token_cookie does
    active_refresh_token = new_refresh_token if new_refresh_token else refresh_token

    csrf_token = generate_csrf_token(active_refresh_token)

    return RefreshResponse(access_token=access_token, csrf_token=csrf_token)


"""
Exposes HTTP endpoints for ending user sessions.
Extracts the active tokens from cookies and headers and delegates to the `LogoutUseCase` to invalidate them.
"""


@router.post(
    "/logout", dependencies=[Depends(verify_csrf)], response_model=MessageResponse
)
async def logout(
    request: Request,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[LogoutUseCase, Depends(get_logout_usecase)],
    jwt_payload: Annotated[dict, Depends(get_jwt_payload)],
):
    """
    Log out the current user and invalidate their session.

    This endpoint securely terminates the user's session by:
    1. Extracting the **Refresh Token** from the `refresh_token` HTTP-Only cookie.
    2. Revoking the refresh token family in the database to prevent future use.
    3. Blacklisting the current access token in Redis by its `jti` until natural expiration.
    4. Instructing the browser to delete the `refresh_token` cookie.

    **Returns:**
    A 200 OK response with a success message.
    """
    refresh_token = request.cookies.get("refresh_token")
    #  Use the already-verified jti/exp from the dependency chain, never re-decode.
    jti = jwt_payload.get("jti")
    exp = jwt_payload.get("exp")

    async with uow:
        await usecase.execute(uow, refresh_token, jti=jti, exp=exp)

    delete_refresh_token_cookie(response)
    return MessageResponse(message="Logged out")


@router.post(
    "/logout/all", dependencies=[Depends(verify_csrf)], response_model=MessageResponse
)
async def logout_all(
    request: Request,
    response: Response,
    user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[LogoutAllUseCase, Depends(get_logout_all_usecase)],
    jwt_payload: Annotated[dict, Depends(get_jwt_payload)],
):
    """
    Log out from every active device / session.

    Revokes all refresh token families for the current user so every session
    (on every device) is immediately invalidated. The current access token is
    blacklisted in Redis and the refresh_token cookie is cleared.

    **Returns:**
    A 200 OK response with a success message.
    """
    # logout_all revokes all refresh tokens for the user; the current access
    # token is also blacklisted by its already-verified jti.
    jti = jwt_payload.get("jti")
    exp = jwt_payload.get("exp")
    async with uow:
        await usecase.execute(uow, user.id, jti=jti, exp=exp)

    delete_refresh_token_cookie(response)
    return MessageResponse(message="Logged out from all devices")
