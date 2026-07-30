from pydantic import BaseModel
from src.modules.projects.presentation.api.schemas.project_read_res import (
    ProjectReadRes,
)


class PaginatedProjectsRes(BaseModel):
    items: list[ProjectReadRes]
    total: int
    page: int
    size: int
