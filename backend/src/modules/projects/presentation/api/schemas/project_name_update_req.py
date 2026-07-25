from pydantic import (
    BaseModel,
)


class ProjectNameUpdateReq(BaseModel):
    name: str
