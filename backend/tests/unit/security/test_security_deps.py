import pytest
from unittest.mock import Mock
from fastapi import Request
import hashlib
from itsdangerous import URLSafeSerializer
from src.core.config import security_settings
from src.modules.auth.authentication.api.dependencies.security import verify_csrf
from src.modules.auth.authentication.domain.exceptions import CSRFValidationException


def test_verify_csrf_success():
    # Setup mock request
    refresh_token = "some-refresh-token"
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    csrf_signer = URLSafeSerializer(security_settings.SESSION_SECRET, salt="csrf-token")
    valid_csrf = csrf_signer.dumps(refresh_token_hash)

    request = Mock(spec=Request)
    request.cookies = {"csrf_token": valid_csrf, "refresh_token": refresh_token}
    request.headers = {"X-CSRF": valid_csrf}

    # Should not raise any exception
    import asyncio

    asyncio.run(
        verify_csrf(
            request,
            csrf_cookie=request.cookies.get("csrf_token"),
            csrf_header=request.headers.get("X-CSRF"),
            refresh_token=request.cookies.get("refresh_token"),
        )
    )


def test_verify_csrf_missing_cookie_or_header():
    request = Mock(spec=Request)
    request.cookies = {"csrf_token": "token"}
    request.headers = {}

    with pytest.raises(CSRFValidationException):
        import asyncio

        asyncio.run(
            verify_csrf(
                request,
                csrf_cookie=request.cookies.get("csrf_token"),
                csrf_header=request.headers.get("X-CSRF"),
                refresh_token=request.cookies.get("refresh_token"),
            )
        )


def test_verify_csrf_mismatch_cookie_header():
    request = Mock(spec=Request)
    request.cookies = {"csrf_token": "token1", "refresh_token": "rt"}
    request.headers = {"X-CSRF": "token2"}

    with pytest.raises(CSRFValidationException):
        import asyncio

        asyncio.run(
            verify_csrf(
                request,
                csrf_cookie=request.cookies.get("csrf_token"),
                csrf_header=request.headers.get("X-CSRF"),
                refresh_token=request.cookies.get("refresh_token"),
            )
        )


def test_verify_csrf_bad_signature():
    refresh_token = "some-refresh-token"
    invalid_csrf = "not.a.valid.signature"

    request = Mock(spec=Request)
    request.cookies = {"csrf_token": invalid_csrf, "refresh_token": refresh_token}
    request.headers = {"X-CSRF": invalid_csrf}

    with pytest.raises(CSRFValidationException):
        import asyncio

        asyncio.run(
            verify_csrf(
                request,
                csrf_cookie=request.cookies.get("csrf_token"),
                csrf_header=request.headers.get("X-CSRF"),
                refresh_token=request.cookies.get("refresh_token"),
            )
        )


def test_verify_csrf_tampered_refresh_token():
    refresh_token = "some-refresh-token"
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    csrf_signer = URLSafeSerializer(security_settings.SESSION_SECRET, salt="csrf-token")
    valid_csrf = csrf_signer.dumps(refresh_token_hash)

    request = Mock(spec=Request)
    request.cookies = {
        "csrf_token": valid_csrf,
        "refresh_token": "different-refresh-token",
    }
    request.headers = {"X-CSRF": valid_csrf}

    with pytest.raises(CSRFValidationException):
        import asyncio

        asyncio.run(
            verify_csrf(
                request,
                csrf_cookie=request.cookies.get("csrf_token"),
                csrf_header=request.headers.get("X-CSRF"),
                refresh_token=request.cookies.get("refresh_token"),
            )
        )
