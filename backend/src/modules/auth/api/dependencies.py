"""
Module: Dependencies
"""

import hashlib
import hmac
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import security_settings
from src.core.container import app_container
from src.core.database import get_db
from src.modules.auth.application.ports.security.access_token import AccessTokenPort
from src.modules.auth.application.use_cases import (
    ExecutePasswordResetUseCase,
    ListSessionsUseCase,
    LoginLocalUserUseCase,
    LogoutAllUseCase,
    LogoutUseCase,
    OAuthCallbackUseCase,
    RefreshSessionUseCase,
    RegisterLocalUserUseCase,
    RequestNewVerificationEmailUseCase,
    RequestPasswordResetUseCase,
    RevokeSessionUseCase,
    VerifyEmailUseCase,
)
from src.modules.auth.application.use_cases.change_password import ChangePasswordUseCase
from src.modules.auth.application.use_cases.tenant_oauth_callback import (
    TenantOAuthCallbackUseCase,
)
from src.modules.auth.domain import UserIdentity
from src.modules.auth.domain.exceptions import (
    CSRFValidationException,
    InvalidTokenException,
    NotAuthenticatedException,
)
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.shared.application.ports.cache import CachePort
from src.shared.domain.enums import UserRole

# =====================================================================
# 1. INFRASTRUCTURE ADAPTERS (Module-level Singletons)
# =====================================================================


def get_cache_adapter() -> CachePort:
    return app_container.cache_adapter


def get_project_repository() -> ProjectQueryRepositoryPort:
    return app_container.project_query_repo


async def get_optional_project_id(
    request: Request,
    api_key: Annotated[str | None, Header(alias="X-Cerberus-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
    cache_adapter: CachePort = Depends(get_cache_adapter),
    project_repo: ProjectQueryRepositoryPort = Depends(get_project_repository),
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

        project = await project_repo.get_by_api_key_hash(db, key_hash)
        project_id = project.id if project else None

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


async def get_required_project_id(
    project_id: Annotated[UUID | None, Depends(get_optional_project_id)],
) -> UUID:
    """Enforces that a Project API key was provided."""
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Project API Key (X-Cerberus-API-Key header) is required.",
        )
    return project_id


async def verify_csrf(request: Request):
    """
    Verifies the Double Submit Cookie for CSRF protection.
    The frontend must extract the non-HttpOnly 'csrf_token' cookie and attach it as the 'X-CSRF' header.
    """
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF")
    refresh_token = request.cookies.get("refresh_token")

    if not csrf_cookie or not csrf_header:
        raise CSRFValidationException()

    # Prevent timing attacks during comparison
    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise CSRFValidationException()

    if not refresh_token:
        return  # No session to protect, so CSRF is not applicable

    csrf_signer = URLSafeSerializer(security_settings.SESSION_SECRET, salt="csrf-token")
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    try:
        bound_hash = csrf_signer.loads(csrf_cookie)
        if not hmac.compare_digest(bound_hash, refresh_token_hash):
            raise CSRFValidationException()
    except BadSignature:
        raise CSRFValidationException()


def get_access_token_adapter() -> AccessTokenPort:
    return app_container.access_token_adapter


async def get_jwt_payload(
    request: Request,
    access_token_adapter: Annotated[AccessTokenPort, Depends(get_access_token_adapter)],
    cache_adapter: Annotated[CachePort, Depends(get_cache_adapter)],
    db: AsyncSession = Depends(get_db),
    project_repo: ProjectQueryRepositoryPort = Depends(get_project_repository),
) -> dict:
    """Extracts, verifies, and returns the raw JWT payload (including custom claims)."""

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise NotAuthenticatedException()

    token = auth_header.removeprefix("Bearer ")

    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        print(f"DECODE ERROR: {e}")
        raise InvalidTokenException()

    print(f"UNVERIFIED PAYLOAD: {unverified_payload}")
    public_key_override = None
    project_id = unverified_payload.get("project_id")
    print(f"PROJECT ID: {project_id}")
    if project_id:
        cache_key = f"project_public_key:{project_id}"
        public_key_override = await cache_adapter.get_string(cache_key)
        print(f"CACHE KEY: {cache_key} -> {public_key_override is not None}")
        if not public_key_override:
            from uuid import UUID

            project = await project_repo.get_by_id(db, UUID(project_id))
            print(f"DB PROJECT: {project.id if project else None}")
            if project and project.public_key:
                public_key_override = project.public_key
                await cache_adapter.set_string(cache_key, public_key_override, ttl=600)
                print("SET CACHE")

    print(f"VERIFYING WITH OVERRIDE: {public_key_override is not None}")
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


async def get_current_user(
    payload: Annotated[dict, Depends(get_jwt_payload)],
) -> UserIdentity:
    """Returns the strongly typed UserIdentity object for normal API endpoints."""
    return payload["_user_obj"]


def require_role(required_role: str | UserRole):
    def role_checker(user: UserIdentity = Depends(get_current_user)):
        if user.role == UserRole.SUPERADMIN:
            return user
        if user.role != required_role and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user

    return role_checker


"""
FastAPI Dependency Injection for Use Cases.

This module provides FastAPI `Depends()`-compatible getter functions for all Use Cases.
By using these functions in the router layer, developers can leverage FastAPI's native
`app.dependency_overrides` mechanism to mock Use Cases during testing, bridging the gap
between Hexagonal Architecture and the FastAPI ecosystem.
"""


def get_register_local_usecase() -> RegisterLocalUserUseCase:
    from src.shared.adapters.logger import AsyncSQLLogger

    return RegisterLocalUserUseCase(
        user_repo=app_container.user_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("RegisterLocalUseCase"),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_login_local_usecase() -> LoginLocalUserUseCase:
    from src.shared.adapters.logger import AsyncSQLLogger

    return LoginLocalUserUseCase(
        user_repo=app_container.user_repo,
        refresh_repo=app_container.refresh_token_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("LoginLocalUseCase"),
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_repo=app_container.project_query_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_change_password_usecase() -> ChangePasswordUseCase:
    from src.shared.adapters.logger import AsyncSQLLogger

    return ChangePasswordUseCase(
        user_repo=app_container.user_repo,
        hasher=app_container.password_hasher,
        logger=AsyncSQLLogger("ChangePasswordUseCase"),
        refresh_repo=app_container.refresh_token_repo,
    )


def get_oauth_callback_usecase() -> OAuthCallbackUseCase:
    return OAuthCallbackUseCase(
        user_repo=app_container.user_repo,
        refresh_repo=app_container.refresh_token_repo,
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_repo=app_container.project_query_repo,
    )


def get_tenant_oauth_callback_usecase():
    return TenantOAuthCallbackUseCase(
        user_repo=app_container.user_repo,
        refresh_repo=app_container.refresh_token_repo,
        email_sender=app_container.auth_email_sender,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
    )


def get_request_new_verification_email_usecase() -> RequestNewVerificationEmailUseCase:
    from src.shared.adapters.logger import AsyncSQLLogger

    return RequestNewVerificationEmailUseCase(
        user_repo=app_container.user_repo,
        logger=AsyncSQLLogger("RequestNewVerificationEmailUseCase"),
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_verify_email_usecase() -> VerifyEmailUseCase:
    from src.shared.adapters.logger import AsyncSQLLogger

    return VerifyEmailUseCase(
        user_repo=app_container.user_repo,
        cache=app_container.cache_adapter,
        logger=AsyncSQLLogger("VerifyEmailUseCase"),
        email_sender=app_container.auth_email_sender,
        refresh_repo=app_container.refresh_token_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_request_password_reset_usecase() -> RequestPasswordResetUseCase:
    from src.core.config import url_settings

    return RequestPasswordResetUseCase(
        user_repo=app_container.user_repo,
        email_sender=app_container.auth_email_sender,
        cache=app_container.cache_adapter,
        frontend_url=url_settings.FRONTEND_URL,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
    )


def get_execute_password_reset_usecase() -> ExecutePasswordResetUseCase:
    return ExecutePasswordResetUseCase(
        user_repo=app_container.user_repo,
        hasher=app_container.password_hasher,
        cache=app_container.cache_adapter,
        refresh_repo=app_container.refresh_token_repo,
        rate_limiter=app_container.rate_limiter,
        turnstile=app_container.turnstile_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_logout_usecase() -> LogoutUseCase:
    return LogoutUseCase(
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
    )


def get_logout_all_usecase() -> LogoutAllUseCase:
    return LogoutAllUseCase(
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
    )


def get_refresh_session_usecase() -> RefreshSessionUseCase:
    return RefreshSessionUseCase(
        refresh_repo=app_container.refresh_token_repo,
        access_token=app_container.access_token_adapter,
        claims_provider=app_container.claims_provider,
        project_repo=app_container.project_query_repo,
    )


def get_list_sessions_usecase() -> ListSessionsUseCase:
    return ListSessionsUseCase(
        refresh_repo=app_container.refresh_token_repo,
    )


def get_revoke_session_usecase() -> RevokeSessionUseCase:
    return RevokeSessionUseCase(
        refresh_repo=app_container.refresh_token_repo,
    )


RegisterLocalUseCaseDep = Annotated[
    RegisterLocalUserUseCase, Depends(get_register_local_usecase)
]
LoginLocalUseCaseDep = Annotated[
    LoginLocalUserUseCase, Depends(get_login_local_usecase)
]
ChangePasswordUseCaseDep = Annotated[
    ChangePasswordUseCase, Depends(get_change_password_usecase)
]
OAuthCallbackUseCaseDep = Annotated[
    OAuthCallbackUseCase, Depends(get_oauth_callback_usecase)
]
RequestNewVerificationEmailUseCaseDep = Annotated[
    RequestNewVerificationEmailUseCase,
    Depends(get_request_new_verification_email_usecase),
]
VerifyEmailUseCaseDep = Annotated[VerifyEmailUseCase, Depends(get_verify_email_usecase)]
RequestPasswordResetUseCaseDep = Annotated[
    RequestPasswordResetUseCase, Depends(get_request_password_reset_usecase)
]
ExecutePasswordResetUseCaseDep = Annotated[
    ExecutePasswordResetUseCase, Depends(get_execute_password_reset_usecase)
]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_usecase)]
LogoutAllUseCaseDep = Annotated[LogoutAllUseCase, Depends(get_logout_all_usecase)]
RefreshSessionUseCaseDep = Annotated[
    RefreshSessionUseCase, Depends(get_refresh_session_usecase)
]
ListSessionsUseCaseDep = Annotated[
    ListSessionsUseCase, Depends(get_list_sessions_usecase)
]
RevokeSessionUseCaseDep = Annotated[
    RevokeSessionUseCase, Depends(get_revoke_session_usecase)
]
