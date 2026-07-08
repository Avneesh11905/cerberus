"""
Exposes HTTP endpoints for refreshing access tokens.
Reads the long-lived refresh token from a secure, HttpOnly cookie,
triggers the `RefreshSessionUseCase`, and returns a fresh short-lived access token.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.authentication.api.schemas import RefreshResponse
from src.authentication.api.usecase_dependencies import get_refresh_session_usecase
from src.authentication.core.usecases import RefreshSessionUseCase
from src.shared.api.dependencies import limiter
from src.shared.api.utils import (
    delete_refresh_token_cookie,
    extract_client_metadata,
    set_refresh_token_cookie,
    generate_csrf_token,
)
from src.shared.config import rate_limit_settings
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow


router = APIRouter()

@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit(rate_limit_settings.REFRESH_RATE_LIMIT)
async def refresh(
    request: Request,
    response: Response,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    usecase: Annotated[RefreshSessionUseCase, Depends(get_refresh_session_usecase)]
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
        access_token, new_refresh_token = await usecase.execute(uow, refresh_token, client_meta=client_meta)
    
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
