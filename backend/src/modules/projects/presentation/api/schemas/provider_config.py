from typing import Any

from pydantic import (
    BaseModel,
)


class ProviderConfig(BaseModel):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None


class MaskedProviderConfig(BaseModel):
    enabled: bool = False
    client_id: str | None = None
    client_secret_configured: bool = False
