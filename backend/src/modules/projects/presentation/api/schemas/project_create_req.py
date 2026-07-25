from pydantic import (
    BaseModel,
)


class ProjectCreateReq(BaseModel):
    name: str
