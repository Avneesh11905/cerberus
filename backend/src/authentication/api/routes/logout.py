"""
Exposes HTTP endpoints for ending user sessions.
Extracts the active tokens from cookies and headers and delegates to the `LogoutUseCase` to invalidate them.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.authentication.api.dependencies import (
    get_current_user,
    get_jwt_payload,
    verify_csrf,
)
from src.authentication.api.schemas import MessageResponse
from src.authentication.api.usecase_dependencies import (
    get_logout_all_usecase,
    get_logout_usecase,
)
from src.authentication.core.domain import UserIdentity
from src.authentication.core.usecases import LogoutUseCase
from src.authentication.core.usecases.logout_all import LogoutAllUseCase
from src.shared.api.dependencies import limiter
from src.shared.api.utils import delete_refresh_token_cookie
from src.shared.config import rate_limit_settings
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


@router.post(
    "/logout", dependencies=[Depends(verify_csrf)], response_model=MessageResponse
)
@limiter.limit(rate_limit_settings.DEFAULT_RATE_LIMIT)
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
@limiter.limit(rate_limit_settings.DEFAULT_RATE_LIMIT)
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
