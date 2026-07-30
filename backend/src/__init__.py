# src root
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.core.config import get_settings
from src.core.container import app_container
from src.modules.projects.infrastructure.tasks import (
    start_project_config_sync_task,
    stop_project_config_sync_task,
)
from src.shared.infrastructure.adapters import AsyncSQLLogger
from src.shared.presentation.api.middlewares import (
    DynamicCORSMiddleware,
    RateLimitAndAnalyticsMiddleware,
)
from src.shared.presentation.api.routes.debug_email import router as debug_email_router
from src.shared.presentation.api.routes.health import router as health_router
from src.api.v1.router import api_router
from src.api.exception_handlers import register_exception_handlers

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
    version=get_settings().core.VERSION,
    docs_url="/docs" if get_settings().core.ENV == "development" else None,
    redoc_url="/redoc" if get_settings().core.ENV == "development" else None,
    openapi_tags=openapi_tags,
    # swagger_favicon_url="/favicon.webp",
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
        get_settings().core.cors_origins_list
        + (dev_origins if get_settings().core.ENV == "development" else [])
    )
)

# Middleware is applied in REVERSE registration order by Starlette.
# The LAST registered middleware is OUTERMOST (runs first on ingress, last on egress).
# Desired ingress order: ProxyHeaders → CORS → GZip → Session
# So we register innermost (Session) first and outermost (ProxyHeaders) last.

app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().security.SESSION_SECRET,
    https_only=(get_settings().core.ENV != "development"),
    same_site="none" if get_settings().core.ENV != "development" else "lax",
)

app.add_middleware(
    DynamicCORSMiddleware,
    fastapi_app=app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS", "PATCH", "DELETE"],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
        "X-CSRF",
        "X-Cerberus-API-Key",
        "CF-Connecting-IP",
    ],
)

# ProxyHeadersMiddleware must be OUTERMOST so every downstream middleware
# (CORS, Session, rate limiting) already sees the real client IP from
# X-Forwarded-For by the time they run.
app.add_middleware(
    RateLimitAndAnalyticsMiddleware,
    core_settings=get_settings().core,
    rate_limit_settings=get_settings().rate_limit,
    rate_limiter=app_container.rate_limiter,
    analytics=app_container.analytics_adapter,
    cache=app_container.cache_adapter,
    default_rate=get_settings().rate_limit.DEFAULT,
    auth_rate=get_settings().rate_limit.AUTH,
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(api_router)
app.include_router(health_router)
if get_settings().core.ENV in ("development", "test"):
    app.include_router(debug_email_router)
