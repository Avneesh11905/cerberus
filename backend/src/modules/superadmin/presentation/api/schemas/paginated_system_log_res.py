from .system_log_res import SystemLogRes

from pydantic import BaseModel


class PaginatedSystemLogRes(BaseModel):
    items: list[SystemLogRes]
    total: int
    page: int
    size: int
