from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from typing import Literal

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectEnvUpdateReq(BaseModel):
    environment: Literal["development", "production"]
