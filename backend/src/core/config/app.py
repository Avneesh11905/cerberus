from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from .base import _BaseSettings


class URLSettings(_BaseSettings):
    FRONTEND_URL: str = "http://localhost:3000"
    API_BASE_URL: str = "http://localhost:8000"

    @field_validator("FRONTEND_URL", "API_BASE_URL")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")


class CoreSettings(_BaseSettings):
    ENV: str = "development"
    VERSION: str = "1.0"
    CORS_ORIGINS: str | None = None
    SUPERADMIN_EMAIL: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []
        return [
            i.strip().rstrip("/") for i in self.CORS_ORIGINS.split(",") if i.strip()
        ]


class CookieSettings:
    def __init__(self, env: str):
        self.SECURE = env != "development"
        self.HTTP_ONLY = True
        self.SAMESITE = "none" if env != "development" else "lax"
        self.PATH = "/"


class LogSettings(_BaseSettings):
    RETENTION_DAYS: int = 28
    LEVEL: str = "INFO"
    model_config = SettingsConfigDict(
        **(_BaseSettings.model_config | {"env_prefix": "LOG_"})
    )
