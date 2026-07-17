from fastapi import APIRouter
from typing import Annotated
from uuid import UUID
from authlib.integrations.base_client.errors import OAuthError
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from src.core.container import app_container
from src.modules.auth.infrastructure.oauth import PARSERS, PROVIDERS
from src.modules.auth.infrastructure.oauth.dynamic import get_dynamic_oauth_client
from src.modules.auth.api.dependencies import (
    get_cache_adapter,
    get_oauth_callback_usecase,
    get_tenant_oauth_callback_usecase,
)
from src.modules.auth.api.schemas import OAuthPreflightResponse
from src.modules.auth.application.use_cases import (
    OAuthCallbackUseCase,
    TenantOAuthCallbackUseCase,
)
from src.modules.auth.domain.exceptions import (
    InvalidProviderException,
)
from src.modules.projects.infrastructure.models import Project
from src.shared.api.dependencies import UnitOfWorkDeps
from src.shared.api.utils import (
    build_auth_redirect_async,
    extract_client_metadata,
    generate_csrf_token,
    set_refresh_token_cookie,
)
from src.shared.application.ports import CachePort
from src.shared.domain.enums import UserRole
import secrets
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db

from fastapi import Response, status
from pydantic import BaseModel

router = APIRouter()

"""
Exposes HTTP endpoints for OAuth provider redirects for project end-users.
When Google/GitHub sends the user back, this route captures the authorization code,
exchanges it for user details, and triggers the `OAuthCallbackUseCase` to establish a session.

Note: For Cerberus Dashboard (tenant) callbacks, see tenant_oauth.py.
"""


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    uow: UnitOfWorkDeps,
    usecase: Annotated[OAuthCallbackUseCase, Depends(get_oauth_callback_usecase)],
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
):
    """Handles the OAuth callback from the provider."""
    session_state = request.session.pop("oauth_state", {})
    state = request.query_params.get("state")

    #  Always require a session state. An absent/expired session_state must never
    # be treated as a bypass — it means the OAuth flow was not initiated by us.
    if not session_state:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth state. Please restart the login flow.",
        )
    if not state or state != session_state.get("nonce"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")

    project_id_str = session_state.get("project_id") or request.session.get(
        "oauth_project_id"
    )

    if not project_id_str:
        # End-user callback always requires a project context.
        # For Cerberus Dashboard callback, use GET /auth/tenant/callback/{provider} instead.
        raise HTTPException(
            status_code=400,
            detail="No project context found in OAuth session state.",
        )

    project_id = UUID(project_id_str)
    fallback_frontend_url = None

    async with uow:
        result = await uow.session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalars().first()
        if not project:
            raise InvalidProviderException()
        provider_config = project.oauth_config.get(provider, {})
        client_id = provider_config.get("client_id")
        client_secret_enc = provider_config.get("client_secret")
        client_secret = (
            app_container.encryption_adapter.decrypt(client_secret_enc)
            if client_secret_enc
            else None
        )
        if not client_id or not client_secret:
            raise InvalidProviderException()
        oauth_client = get_dynamic_oauth_client(provider, client_id, client_secret)
        fallback_frontend_url = project.frontend_url

    if not oauth_client:
        raise InvalidProviderException()

    if error := request.query_params.get("error"):
        error_desc = request.query_params.get("error_description", error)
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {error_desc}",
        )

    # Trade the code for an access token
    try:
        token = await oauth_client.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {getattr(e, 'description', getattr(e, 'error', str(e)))}",
        )
    # Parse the provider-specific token into our standard format
    parser = PARSERS.get(provider)
    if not parser:
        raise InvalidProviderException()
    user_info = await parser(oauth_client, token)

    client_meta = extract_client_metadata(request)
    role = UserRole.USER

    async with uow:
        user, refresh_token, access_token, is_new_user = await usecase.execute(
            uow,
            user_info,
            client_meta=client_meta,
            project_id=project_id,
            role=role,
        )

    # Resolve the frontend URL to redirect back to
    # 1. Try to use the dynamic origin from the session (validated during login)
    frontend_url = request.session.get("oauth_tenant_url")

    # 2. Fallback to the statically configured frontend_url we cached earlier
    if not frontend_url and fallback_frontend_url:
        frontend_url = fallback_frontend_url

    # Clean up session
    request.session.pop("oauth_project_id", None)
    request.session.pop("oauth_tenant_url", None)

    # Store the refresh token in Redis under a short-lived one-time code and redirect
    # to {frontend}/auth/callback?code=<code>. The frontend redeems the code via
    # POST /auth/exchange, which fires with the correct Origin header so cookies are
    # set host-only on cerberus-api without any broad domain bleed.
    return await build_auth_redirect_async(
        refresh_token=refresh_token,
        cache=cache,
        is_new_user=is_new_user,
        access_token=access_token,
        user_id=str(user.id),
        frontend_url=frontend_url,
    )


"""
Exposes HTTP endpoints for OAuth2 social login flows for project end-users.

Two initiation strategies are supported:

1. **Preflight + session** (preferred, secure):
   POST /auth/oauth/preflight/{provider} — SDK calls this via Axios with the
   X-Cerberus-API-Key header. The server validates the key, stores the project_id
   in the signed session cookie, and returns a clean redirect URL with no secrets.
   The SDK then redirects the browser to that URL. GET /auth/login/{provider} then
   reads the project context from the session cookie instead of a query param.

2. **Direct query param** (legacy / non-SDK callers):
   GET /auth/login/{provider}?api_key=cerb_xxx — kept for backwards compatibility.
   The api_key appears in browser history; prefer the preflight flow.

Note: For Cerberus Dashboard (tenant) login, see tenant_oauth.py.
"""


def _origin_from_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


async def _resolve_project_for_oauth(
    provider: str,
    project_id: UUID,
    request: Request,
    db: AsyncSession,
):
    """
    Shared helper: given a resolved project_id, validate the OAuth provider config
    and write oauth_project_id + oauth_tenant_url into the session.
    Returns the configured oauth_client. Raises HTTPException on any failure.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    provider_config = project.oauth_config.get(provider, {})
    client_id = provider_config.get("client_id")
    client_secret_enc = provider_config.get("client_secret")
    client_secret = (
        app_container.encryption_adapter.decrypt(client_secret_enc)
        if client_secret_enc
        else None
    )
    if not provider_config.get("enabled") or not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Provider not available")

    request.session["oauth_project_id"] = str(project_id)

    # Validate and persist the request origin so the callback can redirect back safely.
    request_origin = _origin_from_url(
        request.headers.get("origin")
    ) or _origin_from_url(request.headers.get("referer"))
    allowed_origins = {origin.rstrip("/") for origin in (project.allowed_origins or [])}
    if request_origin and request_origin in allowed_origins:
        request.session["oauth_tenant_url"] = request_origin

    return get_dynamic_oauth_client(provider, client_id, client_secret)


@router.post(
    "/oauth/preflight/{provider}",
    status_code=200,
    response_model=OAuthPreflightResponse,
)
async def oauth_preflight(
    provider: str, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Establish OAuth session context without exposing the API key in a browser URL.

    The SDK calls this endpoint via Axios (which sends X-Cerberus-API-Key as a
    header, never in a URL). The server validates the key, stores the project
    context in the signed session cookie, and returns the redirect URL.
    The SDK then redirects the browser to that URL. Because the session cookie
    carries the project context, GET /auth/login/{provider} needs no api_key
    query parameter.

    **Returns:**
    `{ "redirect_url": "/auth/login/{provider}" }`
    """
    api_key = request.headers.get("X-Cerberus-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not api_key.startswith("cerb_"):
        raise HTTPException(status_code=401, detail="Invalid API Key format")

    key_hash = app_container.api_key_adapter.hash(api_key)
    result = await db.execute(select(Project).where(Project.api_key_hash == key_hash))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Validate provider config eagerly so the caller gets an error now, not after redirect
    provider_config = project.oauth_config.get(provider, {})
    client_id = provider_config.get("client_id")
    client_secret_enc = provider_config.get("client_secret")
    client_secret = (
        app_container.encryption_adapter.decrypt(client_secret_enc)
        if client_secret_enc
        else None
    )
    if not provider_config.get("enabled") or not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Provider not available")

    # Store project ID in a dedicated preflight key (single-use, consumed by GET /auth/login/{provider})
    request.session["oauth_preflight_project_id"] = str(project.id)

    redirect_path = str(request.url_for("login", provider=provider))
    return OAuthPreflightResponse(redirect_url=redirect_path)


@router.get("/login/{provider}")
async def login(
    provider: str,
    request: Request,
    api_key: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Redirect the browser to the OAuth provider's authorization page.

    Resolves the tenant project in two ways (checked in order):
    1. Session cookie set by a prior POST /auth/oauth/preflight/{provider} call
       (preferred — API key never appears in the URL).
    2. `api_key` query parameter (legacy — kept for backwards compatibility).
    """
    project_id = None

    # 1. Preferred path: project context was pre-established by the preflight endpoint
    preflight_project_id = request.session.get("oauth_preflight_project_id")
    if preflight_project_id:
        project_id = UUID(preflight_project_id)
        # Consume the preflight token (single-use)
        request.session.pop("oauth_preflight_project_id", None)

    # 2. Legacy path: api_key in query string
    if project_id is None and api_key:
        if not api_key.startswith("cerb_"):
            raise HTTPException(status_code=401, detail="Invalid API Key format")
        key_hash = app_container.api_key_adapter.hash(api_key)
        result = await db.execute(
            select(Project).where(Project.api_key_hash == key_hash)
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        project_id = project.id

    if not project_id:
        # End-user login always requires a project context.
        # For Cerberus Dashboard login, use GET /auth/tenant/login/{provider} instead.
        raise HTTPException(
            status_code=400,
            detail="No project context found. Provide X-Cerberus-API-Key or use the preflight flow.",
        )

    oauth_client = await _resolve_project_for_oauth(provider, project_id, request, db)

    nonce = secrets.token_urlsafe(16)
    request.session["oauth_state"] = {
        "project_id": str(project_id),
        "nonce": nonce,
    }

    return await oauth_client.authorize_redirect(
        request, str(request.url_for("oauth_callback", provider=provider)), state=nonce
    )


"""
Exposes HTTP endpoints for Cerberus Dashboard (tenant) OAuth login.

Tenants are the developers/organizations that own projects on the platform.
They log in using globally configured OAuth credentials (from .env), with no
API key required — there is no project context at this stage.

Routes:
    GET  /auth/tenant/login/{provider}     — redirect browser to provider
    GET  /auth/tenant/callback/{provider}  — provider redirects back here
"""


@router.get("/tenant/login/{provider}")
async def tenant_login(provider: str, request: Request):
    """
    Redirect the browser to the OAuth provider for Cerberus Dashboard login.

    Uses globally configured provider credentials from .env.
    No API key or project context needed — tenants log into the platform itself.
    """
    oauth_client = PROVIDERS.get(provider)
    if not oauth_client:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    nonce = secrets.token_urlsafe(16)
    request.session["tenant_oauth_state"] = {"nonce": nonce}

    return await oauth_client.authorize_redirect(
        request,
        str(request.url_for("tenant_oauth_callback", provider=provider)),
        state=nonce,
    )


@router.get("/tenant/callback/{provider}")
async def tenant_oauth_callback(
    provider: str,
    request: Request,
    uow: UnitOfWorkDeps,
    usecase: Annotated[
        TenantOAuthCallbackUseCase, Depends(get_tenant_oauth_callback_usecase)
    ],
    cache: Annotated[CachePort, Depends(get_cache_adapter)],
):
    """
    Handle the OAuth provider redirect for Cerberus Dashboard tenant login.
    Validates state, exchanges the code for tokens, upserts the tenant user,
    and redirects to the Cerberus Dashboard.
    """
    session_state = request.session.pop("tenant_oauth_state", {})
    state = request.query_params.get("state")

    if not session_state:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth state. Please restart the login flow.",
        )
    if not state or state != session_state.get("nonce"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")

    oauth_client = PROVIDERS.get(provider)
    if not oauth_client:
        raise InvalidProviderException()

    if error := request.query_params.get("error"):
        error_desc = request.query_params.get("error_description", error)
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {error_desc}",
        )

    try:
        token = await oauth_client.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {getattr(e, 'description', getattr(e, 'error', str(e)))}",
        )

    parser = PARSERS.get(provider)
    if not parser:
        raise InvalidProviderException()
    user_info = await parser(oauth_client, token)

    client_meta = extract_client_metadata(request)

    async with uow:
        user, refresh_token, access_token, is_new_user = await usecase.execute(
            uow,
            user_info,
            client_meta=client_meta,
        )

    return await build_auth_redirect_async(
        refresh_token=refresh_token,
        cache=cache,
        is_new_user=is_new_user,
        access_token=access_token,
        user_id=str(user.id),
    )


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
