from dataclasses import dataclass
from typing import Sequence

from src.modules.superadmin.domain.entities import (
    SystemAnalyticsEntity,
    SystemLogEntity,
    TenantEntity,
)


@dataclass(frozen=True)
class GetSystemAnalyticsDTO:
    analytics: SystemAnalyticsEntity


@dataclass(frozen=True)
class ListTenantsDTO:
    tenants: Sequence[TenantEntity]
    total: int


@dataclass(frozen=True)
class ListTenantLogsDTO:
    logs: Sequence[SystemLogEntity]
    total: int


@dataclass(frozen=True)
class UpdateTenantGlobalRoleDTO:
    tenant: TenantEntity


@dataclass(frozen=True)
class UpdateTenantStatusDTO:
    tenant: TenantEntity
