from fastapi import FastAPI
from src.shared.presentation.api.middlewares.cors import DynamicCORSMiddleware
from unittest.mock import MagicMock


def test_dynamic_cors_middleware():
    fastapi_app = FastAPI()
    app = MagicMock()

    middleware = DynamicCORSMiddleware(
        app=app,
        fastapi_app=fastapi_app,
        allow_origins=["http://static.com"],
    )

    # 1. Statically configured origin
    assert middleware.is_allowed_origin("http://static.com") is True

    # 2. Not allowed origin
    assert middleware.is_allowed_origin("http://not-allowed.com") is False

    # 3. Dynamic origin configured on fastapi app state
    fastapi_app.state.dynamic_cors_origins = {"http://dynamic.com"}
    assert middleware.is_allowed_origin("http://dynamic.com") is True

    # 4. Another not allowed origin after dynamic config
    assert middleware.is_allowed_origin("http://still-not-allowed.com") is False
