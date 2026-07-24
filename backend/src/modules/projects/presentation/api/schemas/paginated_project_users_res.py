from typing import Any

from pydantic import (
    BaseModel,
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


class PaginatedProjectUsersRes(BaseModel):
    items: list[Any]  # Will hold UserProfile at runtime but we can type as Any or dict
    total: int
    page: int
    size: int
