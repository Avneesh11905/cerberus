from pydantic import (
    BaseModel,
)


class ProjectRotateRsaKeysRes(BaseModel):
    public_key: str
