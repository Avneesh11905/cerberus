from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.core.container import app_container
from src.modules.auth.authentication.api.dependencies.core import get_cache_adapter
from src.modules.auth.authentication.api.dependencies.security import (
    get_current_user,
    get_jwt_payload,
    verify_csrf,
)
from src.modules.auth.authentication.api.dependencies.use_cases import (
    get_session_list_usecase,
    get_session_logout_all_usecase,
    get_session_logout_usecase,
    get_session_refresh_usecase,
    get_session_revoke_usecase,
)
from src.modules.auth.authentication.api.schemas import (
    MessageResponse,
    RefreshResponse,
    SessionResponse,
)
from src.modules.auth.authentication.application.use_cases import (
    SessionListUseCase,
    SessionLogoutAllUseCase,
    SessionLogoutUseCase,
    SessionRefreshUseCase,
    SessionRevokeUseCase,
)
from src.modules.auth.authentication.domain.entities import UserIdentity
from src.modules.auth.authentication.domain.exceptions import SessionNotFoundException
from src.shared.api.dependencies import UnitOfWorkDeps
from src.shared.api.utils import (
    delete_refresh_token_cookie,
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
)
from src.shared.application.ports import CachePort

router = APIRouter()

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


"""
Exposes the POST /auth/exchange endpoint.

After an OAuth login, the callback stores the refresh token in Redis under a
short-lived one-time code and redirects the browser to
{frontend}/auth/callback?code=<code>&new_user=<bool>.

The frontend redeems the code here. Because this request originates from the
frontend JS (not an OAuth provider redirect), the Origin header is correct and
cookies are set host-only on cerberus-api. No broad cookie domain is ever needed.
"""


class ExchangeRequest(BaseModel):
    code: str


class ExchangeResponse(BaseModel):
    is_new_user: bool
    csrf_token: str
    access_token: str
    user: dict
    """CSRF token to store in memory on clients that cannot read it from document.cookie
    (i.e. SDK consumers on foreign domains). Must be sent as the X-CSRF header on all
    subsequent state-mutating requests.
    """


@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(
    request: Request,
    response: Response,
    body: ExchangeRequest,
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
    uow: UnitOfWorkDeps,
):
    """
    Redeem a one-time exchange code for session cookies.

    After an OAuth login the browser is redirected to the frontend with a short-lived
    code. The frontend calls this endpoint to convert that code into a refresh token
    cookie (HttpOnly) and a CSRF cookie. The code is consumed immediately on use.

    No CSRF check is required here because:
    - The code is a one-time UUID generated during the OAuth callback
    - It expires in 2 minutes
    - It is transmitted in a JSON body (not a form), which cannot be forged cross-site
    """
    data = await cache.get_dict(f"exchange_code:{body.code}")
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired exchange code",
        )

    # One-time use — delete immediately before setting cookies
    await cache.delete_key(f"exchange_code:{body.code}")

    refresh_token: str = data["refresh_token"]
    is_new_user: bool = data.get("is_new_user", False)
    access_token: str = data.get("access_token", "")
    user_id_str: str | None = data.get("user_id")

    profile = None
    if user_id_str:
        user_repo = app_container.user_profile_repo
        async with uow:
            profile = await user_repo.get_profile(uow.session, UUID(user_id_str))

    set_refresh_token_cookie(response, refresh_token)

    # Derive the CSRF token the same way set_refresh_token_cookie does so that
    # SDK clients on foreign domains (who cannot read document.cookie across
    # origins) can store it in memory and attach it as X-CSRF on future requests.
    csrf_token = generate_csrf_token(refresh_token)

    return ExchangeResponse(
        is_new_user=is_new_user,
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump() if profile else {},
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    request: Request,
    user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: UnitOfWorkDeps,
    usecase: Annotated[SessionListUseCase, Depends(get_session_list_usecase)],
):
    """
    List all active sessions (devices) for the current user.

    This endpoint queries the database for all active refresh token families associated with the user.
    It returns metadata about each session, such as:
    - `ip_address`: The IP address where the session originated.
    - `user_agent`: The browser or device used.
    - `created_at`: When the session was first established.
    - `last_active`: When the session was last refreshed.
    - `is_current`: A boolean indicating if this specific session matches the refresh token provided in the current request's cookies.

    **Returns:**
    A list of session metadata objects.
    """
    current_token = request.cookies.get("refresh_token")
    async with uow:
        sessions = await usecase.execute(uow, user.id, current_token)
    return sessions


@router.delete("/sessions/{family_id}", status_code=204)
async def revoke_session(
    family_id: UUID,
    request: Request,
    user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: UnitOfWorkDeps,
    usecase: Annotated[SessionRevokeUseCase, Depends(get_session_revoke_usecase)],
):
    """
    Revoke a specific session by its Family ID.

    This allows a user to remotely log out of other devices. It immediately invalidates the entire refresh token family associated with that device, forcing the device to re-authenticate on its next request.

    **Returns:**
    A 204 No Content response on success.
    Raises a 404 error if the session family ID does not exist or does not belong to the user.
    """
    try:
        async with uow:
            await usecase.execute(uow, user.id, family_id)
    except Exception as e:
        if isinstance(e, SessionNotFoundException):
            raise HTTPException(status_code=404, detail=str(e))
        raise  # INFO-1: bare raise preserves the original traceback
