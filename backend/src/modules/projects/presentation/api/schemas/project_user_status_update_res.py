from uuid import UUID

from pydantic import (
    BaseModel,
)


class ProjectUserStatusUpdateRes(BaseModel):
    message: str
    user_id: UUID
    is_active: bool
