from typing import Literal

from pydantic import (
    BaseModel,
)


class ProjectEnvUpdateReq(BaseModel):
    environment: Literal["development", "production"]
