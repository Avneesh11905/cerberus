import sys
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from src.shared.api.middleware import DynamicCORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.authentication.api.routes import auth_router
from src.authentication.infrastructure.tasks import (
    start_token_cleanup_task,
    start_user_cleanup_task,
    stop_token_cleanup_task,
    stop_user_cleanup_task,
)
from src.projects.infrastructure.tasks import (
    start_project_config_sync_task,
    stop_project_config_sync_task,
)
from src.shared.adapters.logger import (
    AsyncSQLLogger,
    start_log_worker_task,
    stop_log_worker_task,
)
from src.shared.api.dependencies import limiter
from src.shared.api.routes.debug_email import router as debug_email_router
from src.shared.api.routes.health import router as health_router
from src.shared.config import (
    app_settings,
)
from src.shared.core.exceptions import register_exception_handlers
from src.shared.infrastructure.tasks import (
    start_log_cleanup_task,
    stop_log_cleanup_task,
)
from src.users.api.routes import users_router
from src.projects.api.routes import projects_router
from src.admin.api.routes import admin_router

logger = AsyncSQLLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    is_testing = "pytest" in sys.modules
    if not is_testing:
        start_token_cleanup_task()  # Start the 24-hour cron job that deletes expired refresh tokens
        start_user_cleanup_task()  # Start the 24-hour cron job that deletes unverified user accounts
        start_log_cleanup_task()  # Start the cron job that cleans up old system logs from the DB
        start_log_worker_task()  # Start the background queue worker that flushes active logs to the DB in batches
        start_project_config_sync_task(
            app
        )  # Starts the project config sync background task
    yield
    # Gracefully shut down all background tasks before the app exits
    stop_token_cleanup_task()
    stop_user_cleanup_task()
    stop_log_cleanup_task()
    stop_log_worker_task()
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
    version="0.1.0",
    docs_url="/docs" if app_settings.ENV == "development" else None,
    redoc_url="/redoc" if app_settings.ENV == "development" else None,
    openapi_tags=openapi_tags,
    swagger_favicon_url="/favicon.ico",
    lifespan=lifespan,
)

app.state.limiter = limiter
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
        app_settings.cors_origins_list
        + (dev_origins if app_settings.ENV == "development" else [])
    )
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

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    SessionMiddleware,
    secret_key=app_settings.SESSION_SECRET,
    https_only=(app_settings.ENV != "development"),
    same_site="none" if app_settings.ENV != "development" else "lax",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(health_router)
app.include_router(projects_router)
app.include_router(admin_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("src/static/favicon.webp", media_type="image/webp")


if app_settings.ENV == "development":
    app.include_router(debug_email_router)
