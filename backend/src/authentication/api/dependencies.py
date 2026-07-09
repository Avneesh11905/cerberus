"""
Module: Dependencies
"""

import hashlib
import hmac
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.authentication.container import get_container
from src.authentication.core.domain import UserIdentity
from src.authentication.core.domain.exceptions import (
    CSRFValidationException,
    InvalidTokenException,
    NotAuthenticatedException,
)
from src.authentication.core.domain.user import UserRole
from src.authentication.core.ports.security.access_token import AccessTokenPort
from src.shared.config import app_settings
from src.shared.core.ports.cache import CachePort
from src.shared.infrastructure.sql.connection import get_db
from src.shared.infrastructure.sql.tables import Project


async def get_optional_project_id(
    request: Request,
    api_key: Annotated[str | None, Header(alias="X-Cerberus-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
    cache_adapter: CachePort = Depends(get_cache_adapter),
) -> UUID | None:
    if api_key:
        if not api_key.startswith("cerb_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key format",
            )

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        cache_key = f"api_key_hash:{key_hash}"
        cached_project_id = await cache_adapter.get_string(cache_key)
        
        if cached_project_id:
            return UUID(cached_project_id)

        result = await db.execute(
            select(Project.id).where(Project.api_key_hash == key_hash)
        )
        project_id = result.scalar_one_or_none()

        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
            )

        await cache_adapter.set_string(cache_key, str(project_id), ttl=600)
        return project_id

    # No API key means global Cerberus context. This is used by the Cerberus
    # dashboard for tenant/admin auth. Privileged admin APIs must still rely on
    # authenticated user roles rather than a browser-shipped static secret.
    return None


async def verify_csrf(request: Request):
    """
    Verifies the Double Submit Cookie for CSRF protection.
    The frontend must extract the non-HttpOnly 'csrf_token' cookie and attach it as the 'X-CSRF' header.
    """
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF")
    refresh_token = request.cookies.get("refresh_token")

    if not csrf_cookie or not csrf_header:
        raise CSRFValidationException("Missing CSRF token in cookie or header")

    # Prevent timing attacks during comparison
    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise CSRFValidationException("Invalid CSRF token")

    if not refresh_token:
        return  # No session to protect, so CSRF is not applicable

    csrf_signer = URLSafeSerializer(app_settings.SESSION_SECRET, salt="csrf-token")
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    try:
        bound_hash = csrf_signer.loads(csrf_cookie)
        if not hmac.compare_digest(bound_hash, refresh_token_hash):
            raise CSRFValidationException(
                "CSRF token is not bound to the current session"
            )
    except BadSignature:
        raise CSRFValidationException("Invalid or corrupted CSRF token")


def get_access_token_adapter() -> AccessTokenPort:
    return get_container().access_token_adapter


def get_cache_adapter() -> CachePort:
    return get_container().cache_adapter


async def get_jwt_payload(
    request: Request,
    access_token_adapter: Annotated[AccessTokenPort, Depends(get_access_token_adapter)],
    cache_adapter: Annotated[CachePort, Depends(get_cache_adapter)],
) -> dict:
    """Extracts, verifies, and returns the raw JWT payload (including custom claims)."""

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise NotAuthenticatedException()

    token = auth_header.removeprefix("Bearer ")

    user, payload = access_token_adapter.verify(token)
    if not payload or not payload.get("jti") or not payload.get("sub") or not user:
        raise InvalidTokenException("Access token expired or invalid")

    jti = payload["jti"]

    keys_to_check = [f"blacklist:{jti}", f"disabled_user:{user.id}"]
    results = await cache_adapter.mget_strings(keys_to_check)

    if results[0]:
        raise InvalidTokenException("Access token revoked")

    if results[1]:
        raise InvalidTokenException("Account is disabled")

    # Attach the strongly typed UserIdentity so downstream dependencies can access it if needed
    payload["_user_obj"] = user
    return payload


async def get_current_user(
    payload: Annotated[dict, Depends(get_jwt_payload)],
) -> UserIdentity:
    """Returns the strongly typed UserIdentity object for normal API endpoints."""
    return payload["_user_obj"]


def require_role(required_role: str | UserRole):
    def role_checker(user: UserIdentity = Depends(get_current_user)):
        if user.role != required_role and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user

    return role_checker
