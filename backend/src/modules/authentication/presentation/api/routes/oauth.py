from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from src.modules.authentication.application.commands import (
    OAuthExchangeCommand,
    ProjectUserOAuthCallbackCommand,
    ProjectUserOAuthLoginUrlQuery,
    TenantOAuthCallbackCommand,
    TenantOAuthLoginUrlQuery,
)
from src.modules.authentication.domain.exceptions import OAuthFailedException
from src.modules.authentication.presentation.api.dependencies.project import (
    RequiredProjectIdDep,
)
from src.modules.authentication.presentation.api.schemas import (
    ExchangeRequest,
    ExchangeResponse,
    OAuthPreflightResponse,
)
from src.modules.authentication.presentation.api.utils import (
    build_auth_redirect_async,
    generate_csrf_token,
    set_refresh_token_cookie,
)
from src.modules.authentication.wiring import (
    OAuthExchangeUseCaseDep,
    ProjectUserOAuthCallbackUseCaseDep,
    ProjectUserOAuthLoginUrlUseCaseDep,
    TenantOAuthCallbackUseCaseDep,
    TenantOAuthLoginUrlUseCaseDep,
)
from src.shared.presentation.api.dependencies import CacheAdapterDep
from src.shared.presentation.api.utils import extract_client_metadata

router = APIRouter()

"""
Exposes HTTP endpoints for OAuth provider redirects for project end-users.
When Google/GitHub sends the user back, this route captures the authorization code,
exchanges it for user details, and triggers the `ProjectUserOAuthCallbackUseCase` to establish a session.

Note: For Cerberus Dashboard (tenant) callbacks, see tenant_oauth.py.
"""


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    usecase: ProjectUserOAuthCallbackUseCaseDep,
    cache: CacheAdapterDep,
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
        raise HTTPException(
            status_code=400,
            detail="No project context found in OAuth session state.",
        )

    project_id = UUID(project_id_str)
    client_meta = extract_client_metadata(request)
    command = ProjectUserOAuthCallbackCommand(
        provider=provider,
        project_id=project_id,
        request=request,
        client_meta=client_meta,
    )
    (
        user,
        refresh_token,
        access_token,
        is_new_user,
        fallback_frontend_url,
    ) = await usecase.execute(command)

    frontend_url = request.session.get("oauth_tenant_url")

    # 2. Fallback to the statically configured frontend_url we cached earlier
    if not frontend_url and fallback_frontend_url:
        frontend_url = fallback_frontend_url

    # Clean up sessio
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
   POST /auth/oauth/preflight/{provider} — client calls this via Axios with the
   X-Cerberus-API-Key header. The server validates the key, stores the project_id
   in the signed session cookie, and returns a clean redirect URL with no secrets.
   The client then redirects the browser to that URL. GET /auth/login/{provider} then
   reads the project context from the session cookie instead of a query param.

2. **Direct query param** (legacy callers):
   GET /auth/login/{provider}?api_key=cerb_xxx — kept for backwards compatibility.
   The api_key appears in browser history; prefer the preflight flow.

Note: For Cerberus Dashboard (tenant) login, see tenant_oauth.py.
"""


@router.post(
    "/oauth/preflight/{provider}",
    status_code=200,
    response_model=OAuthPreflightResponse,
)
async def oauth_preflight(
    provider: str,
    request: Request,
    project_id: RequiredProjectIdDep,
):
    """
    Establish OAuth session context without exposing the API key in a browser URL.

    The client calls this endpoint via Axios (which sends X-Cerberus-API-Key as a
    header, never in a URL). The server validates the key, stores the project
    context in the signed session cookie, and returns the redirect URL.
    The client then redirects the browser to that URL. Because the session cookie
    carries the project context, GET /auth/login/{provider} needs no api_key
    query parameter.

    **Returns:**
    `{ "redirect_url": "/auth/login/{provider}" }`
    """
    request.session["oauth_preflight_project_id"] = str(project_id)

    redirect_path = str(request.url_for("login", provider=provider))
    return OAuthPreflightResponse(redirect_url=redirect_path)


@router.get("/login/{provider}")
async def login(
    provider: str,
    request: Request,
    usecase: ProjectUserOAuthLoginUrlUseCaseDep,
):
    """
    Redirect the browser to the OAuth provider's authorization page.

    Resolves the tenant project in two ways (checked in order):
    1. Session cookie set by a prior POST /auth/oauth/preflight/{provider} call
       (preferred — API key never appears in the URL).
    """
    project_id = None
    # 1. Preferred path: project context was pre-established by the preflight endpoint
    preflight_project_id = request.session.get("oauth_preflight_project_id")
    if preflight_project_id:
        project_id = UUID(preflight_project_id)
        # Consume the preflight token (single-use)
        request.session.pop("oauth_preflight_project_id", None)

    try:
        command = ProjectUserOAuthLoginUrlQuery(
            request=request,
            provider=provider,
            redirect_uri=str(request.url_for("oauth_callback", provider=provider)),
            project_id=project_id,
            request_origin=request.headers.get("origin")
            or request.headers.get("referer"),
        )
        url, session_data = await usecase.execute(command)
    except OAuthFailedException as e:
        status_code = 401 if "API Key" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))

    # Store the required OAuth state in the user's session
    for key, value in session_data.items():
        request.session[key] = value

    return RedirectResponse(url, status_code=302)


"""
Exposes the POST /auth/exchange endpoint.

After an OAuth login, the callback stores the refresh token in Redis under a
short-lived one-time code and redirects the browser to
{frontend}/auth/callback?code=<code>&new_user=<bool>.

The frontend redeems the code here. Because this request originates from the
frontend JS (not an OAuth provider redirect), the Origin header is correct and
cookies are set host-only on cerberus-api. No broad cookie domain is ever needed.
"""


@router.post("/exchange", response_model=ExchangeResponse)
async def exchange(
    body: ExchangeRequest,
    response: Response,
    usecase: OAuthExchangeUseCaseDep,
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
    try:
        command = OAuthExchangeCommand(code=body.code)
        refresh_token, is_new_user, access_token, profile_dict = await usecase.execute(
            command
        )
    except OAuthFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    set_refresh_token_cookie(response, refresh_token)

    # Derive the CSRF token the same way set_refresh_token_cookie does so that
    # clients on foreign domains (who cannot read document.cookie across
    # origins) can store it in memory and attach it as X-CSRF on future requests.
    csrf_token = generate_csrf_token(refresh_token)

    return ExchangeResponse(
        is_new_user=is_new_user,
        csrf_token=csrf_token,
        access_token=access_token,
        user=profile_dict if profile_dict else {},
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
async def tenant_login(
    provider: str,
    request: Request,
    usecase: TenantOAuthLoginUrlUseCaseDep,
):
    """
    Redirect the browser to the OAuth provider for Cerberus Dashboard login.

    Uses globally configured provider credentials from .env.
    No API key or project context needed — tenants log into the platform itself.
    """
    try:
        command = TenantOAuthLoginUrlQuery(
            request=request,
            provider=provider,
            redirect_uri=str(
                request.url_for("tenant_oauth_callback", provider=provider)
            ),
        )
        url, session_data = await usecase.execute(command)
    except OAuthFailedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch and map any generic errors from the service layer to HTTP 400
        raise HTTPException(status_code=400, detail=str(e))

    # Store the required OAuth state in the user's session
    for key, value in session_data.items():
        request.session[key] = value

    return RedirectResponse(url, status_code=302)


@router.get("/tenant/callback/{provider}")
async def tenant_oauth_callback(
    provider: str,
    request: Request,
    usecase: TenantOAuthCallbackUseCaseDep,
    cache: CacheAdapterDep,
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

    client_meta = extract_client_metadata(request)
    command = TenantOAuthCallbackCommand(
        provider=provider,
        request=request,
        client_meta=client_meta,
    )
    user, refresh_token, access_token, is_new_user = await usecase.execute(command)

    return await build_auth_redirect_async(
        refresh_token=refresh_token,
        cache=cache,
        is_new_user=is_new_user,
        access_token=access_token,
        user_id=str(user.id),
    )
