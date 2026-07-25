from pydantic import (
    BaseModel,
)


class ProjectUserStatusUpdateReq(BaseModel):
    is_active: bool
