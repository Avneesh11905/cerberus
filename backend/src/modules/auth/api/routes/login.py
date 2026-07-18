from fastapi import APIRouter
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request, Response
from src.modules.auth.api.dependencies.use_cases import (
    get_local_login_usecase,
    get_session_logout_all_usecase,
    get_session_logout_usecase,
    get_session_refresh_usecase,
)
from src.modules.auth.api.dependencies.security import (
    get_current_user,
    verify_csrf,
    get_jwt_payload,
)
from src.modules.auth.api.dependencies.project import get_optional_project_id
from src.modules.auth.api.schemas import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshResponse,
)
from src.modules.auth.application.use_cases import (
    SessionRefreshUseCase,
    SessionLogoutAllUseCase,
    SessionLogoutUseCase,
    LocalLoginUseCase,
)
from src.modules.auth.domain.entities import UserIdentity
from src.shared.api.dependencies import get_is_challenged, UnitOfWorkDeps
from src.shared.api.utils import (
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
    delete_refresh_token_cookie,
)


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
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalLoginUseCase, Depends(get_local_login_usecase)],
    project_id: Annotated[UUID, Depends(get_optional_project_id)],
    is_challenged: bool = Depends(get_is_challenged),
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


# ---------------------------------------------------------
# Tenant Authentication (Dashboard - No Project API Key)
# ---------------------------------------------------------


@router.post("/tenant/login", response_model=LoginResponse)
async def login_tenant(
    request: Request,
    req: LoginRequest,
    response: Response,
    uow: UnitOfWorkDeps,
    usecase: Annotated[LocalLoginUseCase, Depends(get_local_login_usecase)],
    is_challenged: bool = Depends(get_is_challenged),
):
    """
    Authenticate a Cerberus tenant dashboard account.
    """
    client_meta = extract_client_metadata(request)
    async with uow:
        profile, refresh_token, access_token = await usecase.execute(
            uow,
            req.email,
            req.password,
            client_meta=client_meta,
            project_id=None,
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


# ---------------------------------------------------------
# Common Utilities
# ---------------------------------------------------------

"""
Exposes HTTP endpoints for refreshing access tokens.
Reads the long-lived refresh token from a secure, HttpOnly cookie,
triggers the `SessionRefreshUseCase`, and returns a fresh short-lived access token.
"""


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: Request,
    response: Response,
    uow: UnitOfWorkDeps,
    usecase: Annotated[SessionRefreshUseCase, Depends(get_session_refresh_usecase)],
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
Extracts the active tokens from cookies and headers and delegates to the `SessionLogoutUseCase` to invalidate them.
"""


@router.post(
    "/logout", dependencies=[Depends(verify_csrf)], response_model=MessageResponse
)
async def logout(
    request: Request,
    response: Response,
    uow: UnitOfWorkDeps,
    usecase: Annotated[SessionLogoutUseCase, Depends(get_session_logout_usecase)],
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
    uow: UnitOfWorkDeps,
    usecase: Annotated[
        SessionLogoutAllUseCase, Depends(get_session_logout_all_usecase)
    ],
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
