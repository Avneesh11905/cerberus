from typing import Any

from src.modules.projects.presentation.api.schemas.provider_config import ProviderConfig, MaskedProviderConfig


def mask_oauth_config(config: dict[str, ProviderConfig | dict[str, Any]] | None) -> dict[str, MaskedProviderConfig]:
    if not config:
        return {}

    masked: dict[str, MaskedProviderConfig] = {}
    for provider, provider_config in config.items():
        if isinstance(provider_config, ProviderConfig):
            provider_dict = provider_config.model_dump()
        elif isinstance(provider_config, dict):
            provider_dict = provider_config
        else:
            # Fallback if somehow it's not a dict or ProviderConfig
            provider_dict = {}

        secret = provider_dict.pop("client_secret", None)
        enabled = provider_dict.get("enabled", False)
        client_id = provider_dict.get("client_id", None)
        
        masked[provider] = MaskedProviderConfig(
            enabled=enabled,
            client_id=client_id,
            client_secret_configured=bool(secret)
        )

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
