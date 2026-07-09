"""
Exposes the POST /auth/exchange endpoint.

After an OAuth login, the callback stores the refresh token in Redis under a
short-lived one-time code and redirects the browser to
{frontend}/auth/callback?code=<code>&new_user=<bool>.

The frontend redeems the code here. Because this request originates from the
frontend JS (not an OAuth provider redirect), the Origin header is correct and
cookies are set host-only on cerberus-api. No broad cookie domain is ever needed.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.authentication.api.dependencies import get_cache_adapter
from src.shared.api.dependencies import limiter
from src.shared.api.utils import generate_csrf_token, set_refresh_token_cookie
from src.shared.config import rate_limit_settings
from src.shared.core.ports.cache import CachePort
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow
from src.users.container import user_profile_repository


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


router = APIRouter()


@router.post("/exchange", response_model=ExchangeResponse)
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
async def exchange(
    request: Request,
    response: Response,
    body: ExchangeRequest,
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
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
        async with uow:
            profile = await user_profile_repository.get_profile(
                uow.session, UUID(user_id_str)
            )

    set_refresh_token_cookie(response, refresh_token)

    # Derive the CSRF token the same way set_refresh_token_cookie does so that
    # SDK clients on foreign domains (who cannot read document.cookie across
    # origins) can store it in memory and attach it as X-CSRF on future requests.
    csrf_token = generate_csrf_token(refresh_token)

    return ExchangeResponse(
        is_new_user=is_new_user,
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile.model_dump(mode="json") if profile else {},
    )
