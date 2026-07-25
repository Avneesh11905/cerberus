from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from uuid import UUID

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectUserStatusUpdateRes(BaseModel):
    message: str
    user_id: UUID
    is_active: bool
