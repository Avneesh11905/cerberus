"""
Contains shared utility functions for the API layer.
Includes custom response formatters and generic error handlers to maintain a consistent JSON structure across the entire app.
"""

import hashlib
import uuid

from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from itsdangerous import URLSafeSerializer

from src.authentication.core.domain.session import ClientMetadata
from src.shared.config import (
    app_settings,
    cookie_settings,
    token_settings,
    url_settings,
)


def extract_client_metadata(request: Request) -> ClientMetadata:
    """Extracts IP address and User-Agent from the incoming request."""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return ClientMetadata(ip_address=ip, user_agent=ua)


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """
    Standardized utility to set the refresh token cookie and CSRF double-submit cookie.

    Cookies are always host-only (no domain attribute). With SameSite=None they are
    still sent cross-origin from any frontend to cerberus-api, but they never bleed
    to unrelated subdomains. The CSRF token is also host-only so JS on other subdomains
    cannot read it.
    """
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=cookie_settings.HTTP_ONLY,
        secure=cookie_settings.SECURE,
        samesite=cookie_settings.SAMESITE,  # type: ignore
        max_age=token_settings.REFRESH_TOKEN_LIFETIME_DAYS * 86400,
        path=cookie_settings.PATH,
    )

    # Set the CSRF double-submit cookie (MUST be httponly=False so JS can read it).
    # Host-only is safe here: JS on cerberus.aymahajan.in cannot read a cookie that
    # was set on cerberus-api.aymahajan.in — BUT the frontend never needs to read it
    # directly on page load. It is supplied by the /auth/exchange response, which is
    # the first API call made after OAuth. For subsequent CSRF-protected calls the
    # frontend reads it from the cookie jar of the API origin via the exchange response.
    # See the note in api.ts for how this is handled.
    csrf_token = generate_csrf_token(refresh_token)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=cookie_settings.SECURE,
        samesite=cookie_settings.SAMESITE,  # type: ignore
        #  Must match refresh_token lifetime so the CSRF cookie survives browser restarts.
        # Without max_age the CSRF cookie is a session cookie and is lost on restart while
        # the HttpOnly refresh_token cookie (which has max_age) persists, causing CSRF failures.
        max_age=token_settings.REFRESH_TOKEN_LIFETIME_DAYS * 86400,
        path=cookie_settings.PATH,
    )


def delete_refresh_token_cookie(response: Response) -> None:
    """Standardized utility to delete the session cookies."""
    response.delete_cookie(
        key="refresh_token",
        httponly=cookie_settings.HTTP_ONLY,
        secure=cookie_settings.SECURE,
        samesite=cookie_settings.SAMESITE,  # type: ignore
        path=cookie_settings.PATH,
    )
    response.delete_cookie(
        key="csrf_token",
        httponly=False,
        secure=cookie_settings.SECURE,
        samesite=cookie_settings.SAMESITE,  # type: ignore
        path=cookie_settings.PATH,
    )


def generate_csrf_token(refresh_token: str) -> str:
    """Generate a CSRF token bound to the current refresh token."""
    csrf_signer = URLSafeSerializer(app_settings.SESSION_SECRET, salt="csrf-token")
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    return csrf_signer.dumps(refresh_token_hash)


async def create_exchange_code(
    cache,
    refresh_token: str,
    is_new_user: bool = False,
    access_token: str | None = None,
    user_id: str | None = None,
) -> str:
    """
    Creates a one-time 2-minute token in Redis linking to the refresh_token.
    """
    code = str(uuid.uuid4())
    await cache.set_dict(
        f"exchange_code:{code}",
        {
            "refresh_token": refresh_token,
            "is_new_user": is_new_user,
            "access_token": access_token,
            "user_id": user_id,
        },
        ttl=120,  # 2 minutes — plenty for a browser redirect
    )
    return code


async def build_auth_redirect_async(
    refresh_token: str,
    cache,
    is_new_user: bool = False,
    access_token: str | None = None,
    user_id: str | None = None,
    frontend_url: str | None = None,
) -> RedirectResponse:
    """
    Async version of build_auth_redirect. Stores the token in Redis and returns
    a RedirectResponse pointing at {frontend}/auth/callback?code=<code>&new_user=<bool>.
    No cookies are set on this response.
    """
    base_url = (frontend_url if frontend_url else url_settings.FRONTEND_URL).rstrip("/")
    code = await create_exchange_code(
        cache,
        refresh_token,
        is_new_user=is_new_user,
        access_token=access_token,
        user_id=user_id,
    )
    redirect_url = f"{base_url}/auth/callback?code={code}&new_user={'true' if is_new_user else 'false'}"
    return RedirectResponse(url=redirect_url)
