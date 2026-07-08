"""
Loads generic application configuration from the environment using Pydantic Settings.
Defines global settings like debug mode, host, port, and CORS origins.
"""

from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from .base import _BaseSettings


class URLSettings(_BaseSettings):
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("FRONTEND_URL")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")


def split_origins(v: str | list[str]) -> list[str]:
    if isinstance(v, str):
        return [i.strip() for i in v.split(",") if i.strip()]
    return v


class AppSettings(_BaseSettings):
    ENV: str = "development"
    SESSION_SECRET: str
    ENCRYPTION_KEY: str
    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""
    CORS_ORIGINS: str | None = None
    ADMIN_EMAIL: str | None = None
    ACCOUNT_RETENTION_DAYS: int = 28

    @model_validator(mode="after")
    def load_keys(self) -> "AppSettings":
        keys_dir = Path(__file__).resolve().parent.parent.parent.parent / "keys"
        if not self.JWT_PRIVATE_KEY:
            try:
                self.JWT_PRIVATE_KEY = (keys_dir / "jwt_private.pem").read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError("JWT_PRIVATE_KEY is missing from environment and keys/jwt_private.pem not found.")
        if not self.JWT_PUBLIC_KEY:
            try:
                self.JWT_PUBLIC_KEY = (keys_dir / "jwt_public.pem").read_text(encoding="utf-8")
            except FileNotFoundError:
                raise ValueError("JWT_PUBLIC_KEY is missing from environment and keys/jwt_public.pem not found.")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []
        # Strip whitespace and trailing slashes to prevent subtle CORS failures
        return [
            i.strip().rstrip("/") for i in self.CORS_ORIGINS.split(",") if i.strip()
        ]


class CookieSettings:
    """Non-env cookie settings derived from app_settings."""

    def __init__(self, env: str):
        self.SECURE = env != "development"
        self.HTTP_ONLY = True
        self.SAMESITE = "none" if env != "development" else "lax"
        self.PATH = "/"


class LogSettings(_BaseSettings):
    RETENTION_DAYS: int = 28

    model_config = SettingsConfigDict(
        **(_BaseSettings.model_config | {"env_prefix": "LOG_"})
    )
