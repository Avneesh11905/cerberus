from typing import Any
from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config

from pydantic import (
    field_validator,
    BaseModel,
)



class PaginatedProjectUsersRes(BaseModel):
    items: list[Any]  # Will hold UserProfile at runtime but we can type as Any or dict
    total: int
    page: int
    size: int
