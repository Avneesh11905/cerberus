from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)



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
                raise ValueError("Origins must use https:// or be http://localhost")
            if parsed.scheme not in ("http", "https"):
                raise ValueError("Origins must use https:// or be http://localhost")
            if parsed.scheme == "http" and parsed.hostname != "localhost":
                raise ValueError("Origins must use https:// or be http://localhost")
        return origins
