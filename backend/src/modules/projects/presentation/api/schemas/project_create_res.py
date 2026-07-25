from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from datetime import datetime
from uuid import UUID

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectCreateRes(BaseModel):
    id: UUID
    name: str
    api_key: str
    public_key: str
    created_at: datetime
