from .provider_config import ProviderConfig

from pydantic import (
    BaseModel,
)


class ProjectOauthUpdateReq(BaseModel):
    oauth_config: dict[str, ProviderConfig]
