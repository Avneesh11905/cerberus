"""
Defines a global hierarchy for Domain Exceptions.
These custom exceptions abstract away HTTP status codes and presentation logic from the core business logic.
The API layer catches them and translates them into appropriate HTTP responses based on the environment.
"""

import traceback
from typing import Type

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import core_settings

# Auth
from src.modules.auth.domain.exceptions import (
    AuthBaseException,
    CSRFValidationException,
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
    InvalidProviderException,
    InvalidTokenException,
    NotAuthenticatedException,
    OAuthFailedException,
    SamePasswordException,
    SessionNotFoundException,
    UnverifiedEmailException,
)

# Projects
from src.modules.projects.domain.exceptions import (
    ProjectError,
    ProjectForbiddenError,
    ProjectNotFoundError,
)

# Superadmin
from src.modules.superadmin.domain.exceptions import (
    AbsoluteSuperadminImmutableException,
    SuperadminBaseException,
    TenantNotFoundException,
)

# Users
from src.modules.users.domain.exceptions import UserBaseException, UserNotFoundException
from src.shared.adapters.logger import AsyncSQLLogger

logger = AsyncSQLLogger("ExceptionHandlers")


class ExceptionMetadata(BaseModel):
    status_code: int
    dev_detail: str
    prod_detail: str


class RateLimitExceededException(Exception):
    def __init__(self, detail: str, retry_after: int | None = None):
        self.detail = detail
        self.retry_after = retry_after
        super().__init__(detail)


class TurnstileVerificationFailed(AuthBaseException):
    pass


# ==========================================
# EXCEPTION TO HTTP STATUS CODE MAPS
# ==========================================

AUTH_EXCEPTION_STATUS_MAP: dict[Type[AuthBaseException], ExceptionMetadata] = {
    EmailAlreadyRegisteredException: ExceptionMetadata(
        status_code=status.HTTP_409_CONFLICT,
        dev_detail="Registration failed. Email is already in use.",
        prod_detail="Registration failed.",
    ),
    InvalidCredentialsException: ExceptionMetadata(
        status_code=status.HTTP_401_UNAUTHORIZED,
        dev_detail="Invalid email or password.",
        prod_detail="Invalid email or password.",
    ),
    UnverifiedEmailException: ExceptionMetadata(
        status_code=status.HTTP_401_UNAUTHORIZED,
        dev_detail="Invalid email or password (email unverified).",
        prod_detail="Invalid email or password.",
    ),
    InvalidTokenException: ExceptionMetadata(
        status_code=status.HTTP_401_UNAUTHORIZED,
        dev_detail="Invalid or expired token.",
        prod_detail="Invalid or expired token.",
    ),
    NotAuthenticatedException: ExceptionMetadata(
        status_code=status.HTTP_401_UNAUTHORIZED,
        dev_detail="Not authenticated. Missing or invalid credentials.",
        prod_detail="Not authenticated.",
    ),
    CSRFValidationException: ExceptionMetadata(
        status_code=status.HTTP_403_FORBIDDEN,
        dev_detail="CSRF validation failed.",
        prod_detail="CSRF validation failed.",
    ),
    TurnstileVerificationFailed: ExceptionMetadata(
        status_code=status.HTTP_403_FORBIDDEN,
        dev_detail="Turnstile verification failed.",
        prod_detail="Turnstile verification failed.",
    ),
    InvalidProviderException: ExceptionMetadata(
        status_code=status.HTTP_400_BAD_REQUEST,
        dev_detail="Invalid authentication provider specified.",
        prod_detail="Invalid authentication provider.",
    ),
    OAuthFailedException: ExceptionMetadata(
        status_code=status.HTTP_400_BAD_REQUEST,
        dev_detail="OAuth authentication flow failed.",
        prod_detail="OAuth authentication failed.",
    ),
    SessionNotFoundException: ExceptionMetadata(
        status_code=status.HTTP_404_NOT_FOUND,
        dev_detail="Session not found or does not belong to the user.",
        prod_detail="Session not found.",
    ),
    SamePasswordException: ExceptionMetadata(
        status_code=status.HTTP_400_BAD_REQUEST,
        dev_detail="New password must be different from the current password.",
        prod_detail="New password must be different from the current password.",
    ),
}

USER_EXCEPTION_STATUS_MAP: dict[Type[UserBaseException], ExceptionMetadata] = {
    UserNotFoundException: ExceptionMetadata(
        status_code=status.HTTP_404_NOT_FOUND,
        dev_detail="User not found.",
        prod_detail="User not found.",
    ),
}

PROJECT_EXCEPTION_STATUS_MAP: dict[Type[ProjectError], ExceptionMetadata] = {
    ProjectNotFoundError: ExceptionMetadata(
        status_code=status.HTTP_404_NOT_FOUND,
        dev_detail="Project not found.",
        prod_detail="Project not found.",
    ),
    ProjectForbiddenError: ExceptionMetadata(
        status_code=status.HTTP_403_FORBIDDEN,
        dev_detail="Forbidden from accessing this project.",
        prod_detail="Forbidden.",
    ),
}

SUPERADMIN_EXCEPTION_STATUS_MAP: dict[
    Type[SuperadminBaseException], ExceptionMetadata
] = {
    TenantNotFoundException: ExceptionMetadata(
        status_code=status.HTTP_404_NOT_FOUND,
        dev_detail="Tenant not found.",
        prod_detail="Tenant not found.",
    ),
    AbsoluteSuperadminImmutableException: ExceptionMetadata(
        status_code=status.HTTP_403_FORBIDDEN,
        dev_detail="The absolute superadmin role is immutable and cannot be modified.",
        prod_detail="The absolute superadmin role is immutable and cannot be modified.",
    ),
}

# ==========================================
# HANDLERS
# ==========================================


def build_error_response(
    status_code: int, detail: str | list[dict[str, object]] | dict[str, object]
) -> JSONResponse:
    """Helper to build a consistent JSON error response format matching FastAPI standards."""
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def custom_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handles standard HTTP Exceptions raised in the application."""
    await logger.error(
        f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}"
    )
    # Provide slightly sanitized messages for HTTP exceptions in production
    detail = str(exc.detail)
    if core_settings.ENV != "development":
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            detail = "Authentication failed"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            detail = "Forbidden"
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            detail = "Invalid request"
    return build_error_response(exc.status_code, detail)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles Pydantic validation errors nicely."""
    errors: list[dict[str, object]] = []
    for err in exc.errors():
        errors.append(
            {
                "loc": " -> ".join([str(loc) for loc in err.get("loc", [])]),
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
        )
    await logger.warning(f"Validation Error at {request.url.path}: {errors}")
    return build_error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, errors)


async def auth_domain_exception_handler(
    request: Request, exc: AuthBaseException
) -> JSONResponse:
    """Handles all auth-related Domain Exceptions gracefully by dynamically reading their status code and messages."""
    meta = AUTH_EXCEPTION_STATUS_MAP.get(
        type(exc),
        ExceptionMetadata(
            status_code=status.HTTP_400_BAD_REQUEST,
            dev_detail=f"Unhandled Auth Exception: {str(exc)}",
            prod_detail="Authentication operation failed.",
        ),
    )
    detail = meta.dev_detail if core_settings.ENV == "development" else meta.prod_detail

    await logger.warning(
        f"Auth Domain Error ({exc.__class__.__name__}) at {request.url.path}: {detail}"
    )
    return build_error_response(meta.status_code, detail)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unexpected crashes/exceptions."""
    traceback.print_exc()
    await logger.error(f"Unhandled Exception at {request.url.path}: {str(exc)}")
    return build_error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error"
    )


async def user_domain_exception_handler(
    request: Request, exc: UserBaseException
) -> JSONResponse:
    """Handles all user-related Domain Exceptions."""
    meta = USER_EXCEPTION_STATUS_MAP.get(
        type(exc),
        ExceptionMetadata(
            status_code=status.HTTP_400_BAD_REQUEST,
            dev_detail=f"Unhandled User Exception: {str(exc)}",
            prod_detail="User operation failed.",
        ),
    )
    detail = meta.dev_detail if core_settings.ENV == "development" else meta.prod_detail

    await logger.warning(
        f"User Error ({exc.__class__.__name__}) at {request.url.path}: {detail}"
    )
    return build_error_response(meta.status_code, detail)


async def project_domain_exception_handler(
    request: Request, exc: ProjectError
) -> JSONResponse:
    """Handles all project-related Domain Exceptions."""
    meta = PROJECT_EXCEPTION_STATUS_MAP.get(
        type(exc),
        ExceptionMetadata(
            status_code=status.HTTP_400_BAD_REQUEST,
            dev_detail=f"Unhandled Project Exception: {str(exc)}",
            prod_detail="Project operation failed.",
        ),
    )
    detail = meta.dev_detail if core_settings.ENV == "development" else meta.prod_detail

    await logger.warning(
        f"Project Error ({exc.__class__.__name__}) at {request.url.path}: {detail}"
    )
    return build_error_response(meta.status_code, detail)


async def superadmin_domain_exception_handler(
    request: Request, exc: SuperadminBaseException
) -> JSONResponse:
    """Handles all superadmin-related Domain Exceptions."""
    meta = SUPERADMIN_EXCEPTION_STATUS_MAP.get(
        type(exc),
        ExceptionMetadata(
            status_code=status.HTTP_400_BAD_REQUEST,
            dev_detail=f"Unhandled Superadmin Exception: {str(exc)}",
            prod_detail="Superadmin operation failed.",
        ),
    )
    detail = meta.dev_detail if core_settings.ENV == "development" else meta.prod_detail

    await logger.warning(
        f"Superadmin Error ({exc.__class__.__name__}) at {request.url.path}: {detail}"
    )
    return build_error_response(meta.status_code, detail)


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitExceededException
) -> JSONResponse:
    """Handles rate limit exceeded exceptions."""
    await logger.warning(f"Rate Limit Exceeded at {request.url.path}: {exc.detail}")
    headers = {}
    if exc.retry_after is not None:
        headers["Retry-After"] = str(exc.retry_after)

    sanitized = (
        exc.detail
        if core_settings.ENV == "development"
        else "Too many requests. Please try again later."
    )
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": sanitized, "retry_after": exc.retry_after},
        headers=headers,
    )


def register_exception_handlers(app: FastAPI):
    """Registers exception handlers for the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(AuthBaseException, auth_domain_exception_handler)  # type: ignore
    app.add_exception_handler(UserBaseException, user_domain_exception_handler)  # type: ignore
    app.add_exception_handler(ProjectError, project_domain_exception_handler)  # type: ignore
    app.add_exception_handler(
        SuperadminBaseException,
        superadmin_domain_exception_handler,  # type: ignore
    )
    app.add_exception_handler(RateLimitExceededException, rate_limit_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)
