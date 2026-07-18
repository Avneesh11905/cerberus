from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.auth.authorization.domain.enums import GlobalRole
from src.shared.domain.enums import LogLevel


class TenantEntity(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    role: GlobalRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemLogEntity(BaseModel):
    id: UUID
    level: LogLevel
    source: str
    message: str
    file: Optional[str]
    line: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlatformAdoptionMetrics(BaseModel):
    total_tenants: int
    api_requests: int
    registrations: int
    login_successes: int
    login_failures: int
    active_users: int


class EndUserUsageMetrics(BaseModel):
    total_projects: int
    api_requests: int
    registrations: int
    login_successes: int
    login_failures: int
    active_users: int


class SystemAnalyticsEntity(BaseModel):
    platform_adoption: PlatformAdoptionMetrics
    end_user_usage: EndUserUsageMetrics
