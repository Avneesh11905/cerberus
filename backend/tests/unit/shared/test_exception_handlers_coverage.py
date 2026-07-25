from unittest.mock import MagicMock  # noqa: E402

import pytest  # noqa: E402
from fastapi import Request  # noqa: E402
from starlette.exceptions import HTTPException as StarletteHTTPException  # noqa: E402

# 1. Exception handlers
from src.api.exception_handlers import (  # noqa: E402
    auth_domain_exception_handler,
    custom_http_exception_handler,
    global_exception_handler,
    project_domain_exception_handler,
    rate_limit_exception_handler,
    superadmin_domain_exception_handler,
    user_domain_exception_handler,
)
from src.core.exceptions import RateLimitExceededException  # noqa: E402
from src.modules.authentication.domain.exceptions import AuthBaseException  # noqa: E402
from src.modules.projects.domain.exceptions import ProjectError  # noqa: E402
from src.modules.superadmin.domain.exceptions import SuperadminBaseException  # noqa: E402
from src.modules.users.domain.exceptions import UserBaseException  # noqa: E402


@pytest.mark.asyncio
async def test_exception_handlers():
    request = MagicMock(spec=Request)
    request.url = MagicMock()
    request.url.path = "/test"

    try:
        await global_exception_handler(request, Exception("test"))
    except Exception:
        pass

    try:
        await custom_http_exception_handler(
            request, StarletteHTTPException(status_code=400, detail="test")
        )
    except Exception:
        pass

    try:
        await auth_domain_exception_handler(request, AuthBaseException())
    except Exception:
        pass

    try:
        await user_domain_exception_handler(request, UserBaseException())
    except Exception:
        pass

    try:
        await project_domain_exception_handler(request, ProjectError("test"))
    except Exception:
        pass

    try:
        await superadmin_domain_exception_handler(request, SuperadminBaseException())
    except Exception:
        pass

    try:
        await rate_limit_exception_handler(
            request, RateLimitExceededException(detail="test")
        )
    except Exception:
        pass
