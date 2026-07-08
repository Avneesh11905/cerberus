"""
Module: Registry
"""

from typing import Any, Awaitable, Callable, Protocol

from authlib.integrations.starlette_client import OAuth  # type: ignore
from fastapi import Request
from pydantic import BaseModel, Field

from src.authentication.core.domain.user import OAuthUserInfo
from src.shared.adapters.logger import AsyncSQLLogger


class OAuthClientPort(Protocol):
    async def authorize_redirect(
        self, request: Request, redirect_uri: str, **kwargs
    ) -> object: ...
    async def authorize_access_token(
        self, request: Request, **kwargs
    ) -> dict[str, object]: ...


class ProviderMetadata(BaseModel):
    key: str
    display_name: str
    authlib_config: dict[str, Any]
    scopes: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(
        default_factory=lambda: ["client_id", "client_secret"]
    )


logger = AsyncSQLLogger("OAuthRegistry")


class OAuthRegistry:
    def __init__(self):
        self.oauth = OAuth()
        self.providers: dict[str, OAuthClientPort] = {}
        self.parsers: dict[
            str,
            Callable[[OAuthClientPort, dict[str, object]], Awaitable[OAuthUserInfo]],
        ] = {}
        self.metadata: dict[str, ProviderMetadata] = {}

    def register_provider(
        self,
        name: str,
        display_name: str,
        scopes: list[str],
        required_fields: list[str] | None = None,
        **kwargs,
    ):
        """
        Decorator to register a provider, its authlib config, metadata, and user parser.
        """

        def decorator(
            parser_func: Callable[
                [OAuthClientPort, dict[str, object]], Awaitable[OAuthUserInfo]
            ],
        ):
            self.oauth.register(name=name, **kwargs)

            provider_client = getattr(self.oauth, name)
            self.providers[name] = provider_client
            self.parsers[name] = parser_func
            self.metadata[name] = ProviderMetadata(
                key=name,
                display_name=display_name,
                authlib_config=kwargs,
                scopes=scopes,
                required_fields=required_fields or ["client_id", "client_secret"],
            )
            return parser_func

        return decorator


# Global registry instance
oauth_registry = OAuthRegistry()
