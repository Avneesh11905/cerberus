import hashlib
import hmac
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, Request
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature

from src.core.config import get_settings
from src.modules.authentication.application.ports import AuthUoWPort
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.domain.exceptions import (
    CSRFValidationException,
    InvalidTokenException,
    NotAuthenticatedException,
)
from src.modules.authentication.presentation.api.dependencies.core import (
    AccessTokenAdapterDep,
)
from src.modules.authentication.presentation.api.dependencies.authentication_uow_dep import (
    get_auth_uow,
)
from src.shared.presentation.api.dependencies import CacheAdapterDep


async def verify_csrf(
    request: Request,
    csrf_cookie: Annotated[str | None, Cookie(alias="csrf_token")] = None,
    csrf_header: Annotated[str | None, Header(alias="X-CSRF")] = None,
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
):
    """
    Verifies the Double Submit Cookie for CSRF protection.
    The frontend must extract the non-HttpOnly 'csrf_token' cookie and attach it as the 'X-CSRF' header.
    """
    if not csrf_cookie or not csrf_header:
        raise CSRFValidationException()

    # Prevent timing attacks during comparison
    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise CSRFValidationException()

    if not refresh_token:
        return  # No session to protect, so CSRF is not applicable

    csrf_signer = URLSafeSerializer(
        get_settings().security.SESSION_SECRET, salt="csrf-token"
    )
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    try:
        bound_hash = csrf_signer.loads(csrf_cookie)
        if not hmac.compare_digest(bound_hash, refresh_token_hash):
            raise CSRFValidationException()
    except BadSignature:
        raise CSRFValidationException()


async def get_jwt_payload(
    request: Request,
    access_token_adapter: AccessTokenAdapterDep,
    cache_adapter: CacheAdapterDep,
    uow: Annotated[AuthUoWPort, Depends(get_auth_uow)],
) -> dict:
    """Extracts, verifies, and returns the raw JWT payload (including custom claims)."""

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise NotAuthenticatedException()

    token = auth_header.removeprefix("Bearer ")

    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
    except Exception:
        raise InvalidTokenException()

    public_key_override = None
    project_id = unverified_payload.get("project_id")
    if project_id:
        cache_key = f"project_public_key:{project_id}"
        public_key_override = await cache_adapter.get_string(cache_key)
        if not public_key_override:
            from uuid import UUID

            async with uow:
                project = await uow.project_query_repo.get_by_id(UUID(project_id))
            if project and project.public_key:
                public_key_override = project.public_key
                await cache_adapter.set_string(cache_key, public_key_override, ttl=600)

    user, payload = access_token_adapter.verify(
        token, public_key_override=public_key_override
    )
    if not payload or not payload.get("jti") or not payload.get("sub") or not user:
        raise InvalidTokenException()

    jti = payload["jti"]

    keys_to_check = [f"blacklist:{jti}", f"disabled_user:{user.id}"]
    results = await cache_adapter.mget_strings(keys_to_check)

    if results[0]:
        raise InvalidTokenException()

    if results[1]:
        raise InvalidTokenException()

    # Attach the strongly typed UserIdentity so downstream dependencies can access it if needed
    payload["_user_obj"] = user
    return payload


GetJWTPayloadDep = Annotated[dict, Depends(get_jwt_payload)]


async def get_current_user(
    payload: GetJWTPayloadDep,
) -> UserIdentity:
    """Returns the strongly typed UserIdentity object for normal API endpoints."""
    return payload["_user_obj"]


GetCurrentUserDep = Annotated[UserIdentity, Depends(get_current_user)]
VerifyCSRFDep = Depends(verify_csrf)
