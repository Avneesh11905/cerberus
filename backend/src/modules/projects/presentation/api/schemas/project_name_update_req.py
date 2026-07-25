from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectNameUpdateReq(BaseModel):
    name: str
