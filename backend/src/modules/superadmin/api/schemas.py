from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.shared.domain.enums import LogLevel, UserRole


class TenantRes(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedTenantRes(BaseModel):
    items: list[TenantRes]
    total: int
    page: int
    size: int


class TenantStatusUpdateReq(BaseModel):
    is_active: bool


class TenantRoleUpdateReq(BaseModel):
    role: UserRole


class SystemLogRes(BaseModel):
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedSystemLogRes(BaseModel):
    items: list[SystemLogRes]
    total: int
    page: int
    size: int


class AnalyticsMetrics(BaseModel):
    total_tenants: int = 0
    total_projects: int = 0
    api_requests: int = 0
    registrations: int = 0
    login_successes: int = 0
    login_failures: int = 0
    active_users: int = 0
    model_config = ConfigDict(from_attributes=True)


class SystemAnalyticsRes(BaseModel):
    platform_adoption: AnalyticsMetrics
    end_user_usage: AnalyticsMetrics
    model_config = ConfigDict(from_attributes=True)
