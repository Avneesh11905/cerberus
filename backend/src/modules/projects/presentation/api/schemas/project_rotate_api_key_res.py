from pydantic import (
    BaseModel,
)


class ProjectRotateApiKeyRes(BaseModel):
    api_key: str
