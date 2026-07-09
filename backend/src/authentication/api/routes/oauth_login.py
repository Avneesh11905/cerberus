"""
Exposes HTTP endpoints for OAuth2 social login flows.

Two initiation strategies are supported:

1. **Preflight + session** (preferred, secure):
   POST /auth/oauth/preflight/{provider} — SDK calls this via Axios with the
   X-Cerberus-API-Key header. The server validates the key, stores oauth_project_id
   in the signed session cookie, and returns a clean redirect URL with no secrets.
   The SDK then redirects the browser to that URL. GET /auth/login/{provider} then
   reads the project context from the session cookie instead of a query param.

2. **Direct query param** (legacy / non-SDK callers):
   GET /auth/login/{provider}?api_key=cerb_xxx — original flow kept for backwards
   compatibility. The api_key appears in browser history; prefer the preflight flow.
"""

import hashlib
import secrets
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.authentication.api.schemas import OAuthPreflightResponse
from src.authentication.infrastructure.oauth import PROVIDERS
from src.authentication.infrastructure.oauth.dynamic import get_dynamic_oauth_client
from src.shared.api.dependencies import limiter
from src.shared.config import rate_limit_settings
from src.shared.container import shared_container
from src.shared.infrastructure.sql.connection import get_db
from src.shared.infrastructure.sql.tables import Project

router = APIRouter()


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
        shared_container.encryption_adapter.decrypt(client_secret_enc)
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
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
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

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(select(Project).where(Project.api_key_hash == key_hash))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Validate provider config eagerly so the caller gets an error now, not after redirect
    provider_config = project.oauth_config.get(provider, {})
    client_id = provider_config.get("client_id")
    client_secret_enc = provider_config.get("client_secret")
    client_secret = (
        shared_container.encryption_adapter.decrypt(client_secret_enc)
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
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
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
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        result = await db.execute(
            select(Project).where(Project.api_key_hash == key_hash)
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        project_id = project.id

    if project_id:
        oauth_client = await _resolve_project_for_oauth(
            provider, project_id, request, db
        )
    else:
        request.session.pop("oauth_project_id", None)
        oauth_client = PROVIDERS.get(provider)
        if not oauth_client:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    nonce = secrets.token_urlsafe(16)
    request.session["oauth_state"] = {
        "project_id": str(project_id) if project_id else None,
        "nonce": nonce,
    }

    return await oauth_client.authorize_redirect(
        request, str(request.url_for("oauth_callback", provider=provider)), state=nonce
    )
