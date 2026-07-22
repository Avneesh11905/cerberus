from .tenant_res import TenantRes

from pydantic import BaseModel


class PaginatedTenantRes(BaseModel):
    items: list[TenantRes]
    total: int
    page: int
    size: int
