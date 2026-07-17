# src root
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.api.v1_0.router import api_router
from src.core.config import (
    core_settings,
    rate_limit_settings,
    security_settings,
)
from src.core.container import app_container
from src.core.exceptions import register_exception_handlers
from src.modules.projects.infrastructure.tasks import (
    start_project_config_sync_task,
    stop_project_config_sync_task,
)
from src.shared.adapters import AsyncSQLLogger
from src.shared.api.middlewares import (
    DynamicCORSMiddleware,
    RateLimitAndAnalyticsMiddleware,
)
from src.shared.api.routes.debug_email import router as debug_email_router

logger = AsyncSQLLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    is_testing = "pytest" in sys.modules
    if not is_testing:
        # Starts the project config sync background task
        start_project_config_sync_task(app)
    yield
    # Gracefully shut down all background tasks before the app exits
    stop_project_config_sync_task()


openapi_tags = [
    {
        "name": "Auth",
        "description": "Core authentication flows including email/password registration, OAuth2 social logins, OTP email verification, secure session management, and password reset pipelines.",
    },
    {
        "name": "Users",
        "description": "User profile management. Endpoints to fetch, update, and securely delete user accounts and their associated session data.",
    },
]

app = FastAPI(
    title="Cerberus",
    description="The Guardian of Avneesh's Underworld",
    version=core_settings.VERSION,
    docs_url="/docs" if core_settings.ENV == "development" else None,
    redoc_url="/redoc" if core_settings.ENV == "development" else None,
    openapi_tags=openapi_tags,
    # swagger_favicon_url="/favicon.ico",
    lifespan=lifespan,
)

register_exception_handlers(app)

# In dev mode, we automatically whitelist common local frontend ports to save developers headaches
dev_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",  # Create React App / Next.js
    "http://localhost:5173",
    "http://127.0.0.1:5173",  # Vite (React/Vue/Svelte)
    "http://localhost:8000",
    "http://127.0.0.1:8000",  # FastAPI Swagger UI
]
origins = list(
    set(
        core_settings.cors_origins_list
        + (dev_origins if core_settings.ENV == "development" else [])
    )
)

# Middleware is applied in REVERSE registration order by Starlette.
# The LAST registered middleware is OUTERMOST (runs first on ingress, last on egress).
# Desired ingress order: ProxyHeaders → CORS → GZip → Session
# So we register innermost (Session) first and outermost (ProxyHeaders) last.

app.add_middleware(
    SessionMiddleware,
    secret_key=security_settings.SESSION_SECRET,
    https_only=(core_settings.ENV != "development"),
    same_site="none" if core_settings.ENV != "development" else "lax",
)

app.add_middleware(
    DynamicCORSMiddleware,
    fastapi_app=app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS", "PATCH", "DELETE"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-CSRF",
        "X-Cerberus-API-Key",
        "X-Cerberus-Admin-Key",
        "CF-Connecting-IP",
    ],
)

# ProxyHeadersMiddleware must be OUTERMOST so every downstream middleware
# (CORS, Session, rate limiting) already sees the real client IP from
# X-Forwarded-For by the time they run.
app.add_middleware(
    RateLimitAndAnalyticsMiddleware,
    core_settings=core_settings,
    rate_limit_settings=rate_limit_settings,
    rate_limiter=app_container.rate_limiter,
    analytics=app_container.analytics_adapter,
    default_rate=rate_limit_settings.DEFAULT,
    auth_rate=rate_limit_settings.AUTH,
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(api_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("src/shared/static/favicon.webp", media_type="image/webp")


if core_settings.ENV == "development":
    app.include_router(debug_email_router)
