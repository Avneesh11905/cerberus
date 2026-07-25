from pydantic import (
    BaseModel,
)


class ProjectSecretsRes(BaseModel):
    public_key: str
