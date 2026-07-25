from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
)


class ProjectCreateRes(BaseModel):
    id: UUID
    name: str
    api_key: str
    public_key: str
    created_at: datetime
