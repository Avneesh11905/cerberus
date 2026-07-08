from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp


class DynamicCORSMiddleware(CORSMiddleware):
    """
    Subclasses Starlette's CORSMiddleware to allow dynamic origin evaluation.
    It checks the statically configured origins first, and then checks an
    in-memory set on the FastAPI app state that is periodically refreshed.
    """
    def __init__(
        self,
        app: ASGIApp,
        fastapi_app: FastAPI,
        allow_origins: list[str] = ["*"],
        allow_methods: list[str] = ["GET"],
        allow_headers: list[str] = [],
        allow_credentials: bool = False,
        allow_origin_regex: str | None = None,
        expose_headers: list[str] = [],
        max_age: int = 600,
    ) -> None:
        super().__init__(
            app=app,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            allow_origin_regex=allow_origin_regex,
            expose_headers=expose_headers,
            max_age=max_age,
        )
        self.fastapi_app = fastapi_app

    def is_allowed_origin(self, origin: str) -> bool:
        # First check standard static configuration
        if super().is_allowed_origin(origin):
            return True
        
        # Check dynamic origins
        dynamic_origins: set[str] = getattr(self.fastapi_app.state, "dynamic_cors_origins", set())
        return origin in dynamic_origins
