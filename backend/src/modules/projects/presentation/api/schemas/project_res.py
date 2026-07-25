from typing import Any
from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    field_serializer,
    field_validator,
)

from src.core.config import get_settings



class ProjectRes(BaseModel):
    id: UUID
    name: str
    public_key: str
    oauth_config: dict[str, MaskedProviderConfig]
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

    @field_validator("oauth_config", mode="before")
    def validate_oauth_config(cls, v) -> dict[str, MaskedProviderConfig]:
        return mask_oauth_config(v)

    @field_validator("frontend_url", mode="before")
    def extract_frontend_url(cls, v: Any) -> str | None:
        return v.value if hasattr(v, "value") else v
