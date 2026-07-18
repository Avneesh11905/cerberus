"""
Exposes HTTP endpoints for managing user sessions (devices).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from src.modules.auth.api.dependencies.use_cases import (
    get_session_list_usecase,
    get_session_revoke_usecase,
)
from src.modules.auth.api.dependencies.security import get_current_user
from src.modules.auth.api.schemas import SessionResponse
from src.modules.auth.application.use_cases import (
    SessionListUseCase,
    SessionRevokeUseCase,
)
from src.modules.auth.domain.entities import UserIdentity
from src.modules.auth.domain.exceptions import SessionNotFoundException
from src.shared.api.dependencies import UnitOfWorkDeps

router = APIRouter()


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
