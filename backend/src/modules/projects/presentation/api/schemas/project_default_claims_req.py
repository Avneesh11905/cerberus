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
    "exp",
    "iat",
    "jti",
    "project_id",
    "is_verified",
    "family_id",
}


ClaimValue = str | int | bool | float

class ProjectDefaultClaimsReq(BaseModel):
    claims: dict[str, ClaimValue | dict[str, ClaimValue]] = Field(default_factory=dict)

    @field_validator("claims")
    @classmethod
    def validate_claims(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 claim keys")
        forbidden = set(v.keys()) & RESERVED_CLAIM_KEYS
        if forbidden:
            raise ValueError(f"Reserved keys: {forbidden}")
        for key in v:
            if not key.isidentifier():
                raise ValueError(f"Invalid key name: '{key}'")
        return v
