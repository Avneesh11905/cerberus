from typing import Any

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


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


RESERVED_CLAIM_KEYS = {
    "sub",
    "email",
    "role",
    "exp",
    "iat",
    "jti",
    "project_id",
    "is_verified",
    "family_id",
}


class ProjectOriginsUpdateReq(BaseModel):
    allowed_origins: list[str] = Field(max_length=5)

    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        from urllib.parse import urlparse

        for origin in origins:
            if origin == "*":
                continue
            parsed = urlparse(origin)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid origin URL: {origin}")
        return origins
