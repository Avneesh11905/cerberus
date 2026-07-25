from src.modules.projects.presentation.api.schemas.provider_config import MaskedProviderConfig
from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from .provider_config import ProviderConfig

from pydantic import (
    field_validator,
    BaseModel,
)



class ProjectOauthUpdateReq(BaseModel):
    oauth_config: dict[str, ProviderConfig]
