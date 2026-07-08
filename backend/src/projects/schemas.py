from datetime import datetime
from uuid import UUID

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_serializer


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


class ProjectEnvUpdateReq(BaseModel):
    environment: Literal["development", "production"]


class ProjectFrontendUrlUpdateReq(BaseModel):
    frontend_url: str | None = None


class ProjectNameUpdateReq(BaseModel):
    name: str


class ProjectSecretsRes(BaseModel):
    api_key_hash: str
    public_key: str


class ProjectRotateApiKeyRes(BaseModel):
    api_key: str


class ProjectRotateRsaKeysRes(BaseModel):
    public_key: str
