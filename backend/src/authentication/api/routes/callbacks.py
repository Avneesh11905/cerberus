"""
Exposes HTTP endpoints for OAuth provider redirects.
When Google/GitHub sends the user back, this route captures the authorization code,
exchanges it for user details, and triggers the `OAuthCallbackUseCase` to establish a session.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select

from src.authentication.api.dependencies import get_cache_adapter
from src.authentication.api.usecase_dependencies import get_oauth_callback_usecase
from src.authentication.core.domain import UserRole
from src.authentication.core.domain.exceptions import (
    InvalidProviderException,
)
from src.authentication.core.usecases import OAuthCallbackUseCase
from src.authentication.infrastructure.oauth import PARSERS, PROVIDERS
from src.authentication.infrastructure.oauth.dynamic import get_dynamic_oauth_client
from src.shared.api.dependencies import limiter
from src.shared.api.utils import build_auth_redirect_async, extract_client_metadata
from src.shared.config import rate_limit_settings
from src.shared.container import shared_container
from src.shared.core.ports.cache import CachePort
from src.shared.infrastructure.sql.tables import Project
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


@router.get("/callback/{provider}", include_in_schema=False)
@limiter.limit(rate_limit_settings.LOGIN_RATE_LIMIT)
async def oauth_callback(
    provider: str,
    request: Request,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
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
    project_id = None
    fallback_frontend_url = None

    if project_id_str:
        project_id = UUID(project_id_str)
        async with uow:
            result = await uow.session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalars().first()
            if not project:
                raise InvalidProviderException("Associated project not found")
            provider_config = project.oauth_config.get(provider, {})
            client_id = provider_config.get("client_id")
            client_secret_enc = provider_config.get("client_secret")
            client_secret = (
                shared_container.encryption_adapter.decrypt(client_secret_enc)
                if client_secret_enc
                else None
            )
            if not client_id or not client_secret:
                raise InvalidProviderException(
                    f"Provider {provider} is not fully configured for project"
                )
            oauth_client = get_dynamic_oauth_client(provider, client_id, client_secret)
            fallback_frontend_url = project.frontend_url
    else:
        oauth_client = PROVIDERS.get(provider)

    if not oauth_client:
        raise InvalidProviderException(f"Invalid provider: {provider}")

    # Trade the code for an access token
    token = await oauth_client.authorize_access_token(request)
    # Parse the provider-specific token into our standard format
    parser = PARSERS.get(provider)
    if not parser:
        raise InvalidProviderException(f"No parser found for provider: {provider}")
    user_info = await parser(oauth_client, token)

    client_meta = extract_client_metadata(request)
    role = UserRole.TENANT if project_id is None else UserRole.USER

    async with uow:
        user, refresh_token, access_token, is_new_user = await usecase.execute(
            uow,
            user_info,
            client_meta=client_meta,
            project_id=project_id,
            role=role,
        )

    # Resolve the frontend URL to redirect back to
    frontend_url = None
    if project_id:
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
