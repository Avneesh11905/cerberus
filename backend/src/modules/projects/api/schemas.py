from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
)

from src.core.config import url_settings


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


class ProjectCreateReq(BaseModel):
    name: str


class ProjectCreateRes(BaseModel):
    id: UUID
    name: str
    api_key: str
    public_key: str
    created_at: datetime


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

    @computed_field  # type: ignore[misc]
    @property
    def oauth_callback_urls(self) -> dict[str, str]:
        base_url = url_settings.API_BASE_URL.rstrip("/")
        return {
            "google": f"{base_url}/api/v1/auth/oauth/google/callback",
            "github": f"{base_url}/api/v1/auth/oauth/github/callback",
        }

    @field_serializer("oauth_config")
    def serialize_oauth_config(self, oauth_config: dict[str, Any]) -> dict[str, Any]:
        return mask_oauth_config(oauth_config)


class ProjectReadRes(BaseModel):
    id: UUID
    name: str
    oauth_config: dict
    allowed_origins: list[str]
    environment: Literal["development", "production"]
    frontend_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[misc]
    @property
    def oauth_callback_urls(self) -> dict[str, str]:
        base_url = url_settings.API_BASE_URL.rstrip("/")
        return {
            "google": f"{base_url}/api/v1/auth/oauth/google/callback",
            "github": f"{base_url}/api/v1/auth/oauth/github/callback",
        }

    @field_serializer("oauth_config")
    def serialize_oauth_config(self, oauth_config: dict[str, Any]) -> dict[str, Any]:
        return mask_oauth_config(oauth_config)


class ProviderConfig(BaseModel):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None


class ProjectOauthUpdateReq(BaseModel):
    oauth_config: dict[str, ProviderConfig]


class OAuthProviderRes(BaseModel):
    key: str
    display_name: str
    scopes: list[str]
    required_fields: list[str]


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


class ProjectEnvUpdateReq(BaseModel):
    environment: Literal["development", "production"]


class ProjectFrontendUrlUpdateReq(BaseModel):
    frontend_url: str | None = None


class ProjectNameUpdateReq(BaseModel):
    name: str


class ProjectSecretsRes(BaseModel):
    public_key: str


class ProjectUserStatusUpdateReq(BaseModel):
    is_active: bool


class ProjectUserStatusUpdateRes(BaseModel):
    message: str
    user_id: UUID
    is_active: bool


class PaginatedProjectUsersRes(BaseModel):
    items: list[Any]  # Will hold UserProfile at runtime but we can type as Any or dict
    total: int
    page: int
    size: int


class ProjectRotateApiKeyRes(BaseModel):
    api_key: str


class ProjectRotateRsaKeysRes(BaseModel):
    public_key: str


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


class ProjectDefaultClaimsReq(BaseModel):
    claims: dict[str, str | int | bool | float] = Field(default_factory=dict)

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


class ProjectDefaultClaimsRes(BaseModel):
    project_id: UUID
    default_claims: dict[str, Any]


class UserClaimsOverrideReq(BaseModel):
    overrides: dict[str, str | int | bool | float] = Field(default_factory=dict)

    @field_validator("overrides")
    @classmethod
    def validate_overrides(cls, v):
        forbidden = set(v.keys()) & RESERVED_CLAIM_KEYS
        if forbidden:
            raise ValueError(f"Reserved keys: {forbidden}")
        return v


class UserClaimsRes(BaseModel):
    user_id: UUID
    default_claims: dict[str, Any]
    user_overrides: dict[str, Any]
    effective_claims: dict[str, Any]
