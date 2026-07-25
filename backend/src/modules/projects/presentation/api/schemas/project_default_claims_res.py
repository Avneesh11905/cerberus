from typing import Any
from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from uuid import UUID

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectDefaultClaimsRes(BaseModel):
    project_id: UUID
    default_claims: dict[str, Any]
