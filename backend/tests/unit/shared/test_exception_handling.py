import pytest
from unittest.mock import MagicMock
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from src.api.exception_handlers import (
    custom_http_exception_handler,
    validation_exception_handler,
    auth_domain_exception_handler,
    global_exception_handler,
    user_domain_exception_handler,
    project_domain_exception_handler,
    superadmin_domain_exception_handler,
    rate_limit_exception_handler,
)
from src.modules.authentication.domain.exceptions import AuthBaseException
from src.modules.users.domain.exceptions import UserBaseException
from src.modules.projects.domain.exceptions import ProjectError
from src.modules.superadmin.domain.exceptions import SuperadminBaseException
from src.core.exceptions import RateLimitExceededException
from src.core.config import get_settings


@pytest.fixture
def mock_request():
    req = MagicMock(spec=Request)
    req.url.path = "/test-path"
    return req


@pytest.mark.asyncio
async def test_exception_handlers(mock_request):
    # Test HTTP Exception
    exc_http = StarletteHTTPException(status_code=401, detail="Unauthorized test")
    res = await custom_http_exception_handler(mock_request, exc_http)
    assert res.status_code == 401

    # Test Validation Exception
    exc_val = RequestValidationError(
        errors=[
            {
                "loc": ["body", "email"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    )
    res = await validation_exception_handler(mock_request, exc_val)
    assert res.status_code == 422

    # Test Auth Domain Exception
    class CustomAuthException(AuthBaseException):
        pass

    res = await auth_domain_exception_handler(mock_request, CustomAuthException())
    assert res.status_code == 400

    # Test User Domain Exception
    class CustomUserException(UserBaseException):
        pass

    res = await user_domain_exception_handler(mock_request, CustomUserException())
    assert res.status_code == 400

    # Test Project Domain Exception
    class CustomProjectException(ProjectError):
        pass

    res = await project_domain_exception_handler(mock_request, CustomProjectException())
    assert res.status_code == 400

    # Test Superadmin Domain Exception
    class CustomSuperadminException(SuperadminBaseException):
        pass

    res = await superadmin_domain_exception_handler(
        mock_request, CustomSuperadminException()
    )
    assert res.status_code == 400

    # Test Global Exception
    exc_global = Exception("Global error test")
    res = await global_exception_handler(mock_request, exc_global)
    assert res.status_code == 500

    # Test Rate Limit Exception
    exc_rl = RateLimitExceededException(detail="Too many requests", retry_after=60)
    res = await rate_limit_exception_handler(mock_request, exc_rl)
    assert res.status_code == 429
    assert res.headers["Retry-After"] == "60"


@pytest.mark.asyncio
async def test_exception_handlers_prod_env(mock_request, monkeypatch):
    monkeypatch.setattr(get_settings().core, "ENV", "production")

    exc_http = StarletteHTTPException(status_code=401, detail="Unauthorized test")
    res = await custom_http_exception_handler(mock_request, exc_http)
    assert res.status_code == 401

    class CustomAuthException(AuthBaseException):
        pass

    res = await auth_domain_exception_handler(mock_request, CustomAuthException())
    assert res.status_code == 400

    class CustomUserException(UserBaseException):
        pass

    res = await user_domain_exception_handler(mock_request, CustomUserException())
    assert res.status_code == 400

    class CustomProjectException(ProjectError):
        pass

    res = await project_domain_exception_handler(mock_request, CustomProjectException())
    assert res.status_code == 400

    class CustomSuperadminException(SuperadminBaseException):
        pass

    res = await superadmin_domain_exception_handler(
        mock_request, CustomSuperadminException()
    )
    assert res.status_code == 400

    exc_rl = RateLimitExceededException(detail="Too many requests")
    res = await rate_limit_exception_handler(mock_request, exc_rl)
    assert res.status_code == 429
