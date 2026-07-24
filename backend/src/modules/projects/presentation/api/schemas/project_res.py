from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    field_serializer,
    field_validator,
)

from src.core.config import get_settings


def mask_oauth_config(config: dict[str, Any] | None) -> dict[str, Any]:
    if not config:
        return {}

    masked: dict[str, Any] = {}
    for provider, provider_config in config.items():
        if not isinstance(provider_config, dict):
            masked[provider] = provider_config
            continue

        safe_config = dict(provider_config)
        secret = safe_config.pop("client_secret", None)
        safe_config["client_secret_configured"] = bool(secret)
        masked[provider] = safe_config

    return masked



class ProjectRes(BaseModel):
    id: UUID
    name: str
    public_key: str
    oauth_config: dict[str, Any]
    allowed_origins: list[str]
    environment: Literal["development", "production"]
    frontend_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def oauth_callback_urls(self) -> dict[str, str]:
        base_url = get_settings().url.API_BASE_URL.rstrip("/")
        return {
            "google": f"{base_url}/api/v1/auth/oauth/google/callback",
            "github": f"{base_url}/api/v1/auth/oauth/github/callback",
        }

    @field_serializer("oauth_config")
    def serialize_oauth_config(self, oauth_config: dict[str, Any]) -> dict[str, Any]:
        return mask_oauth_config(oauth_config)

    @field_validator("frontend_url", mode="before")
    def extract_frontend_url(cls, v: Any) -> str | None:
        return v.value if hasattr(v, "value") else v
