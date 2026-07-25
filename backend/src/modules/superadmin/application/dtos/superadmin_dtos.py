from dataclasses import dataclass

from src.modules.superadmin.domain.entities import TenantEntity


@dataclass(frozen=True)
class UpdateTenantGlobalRoleDTO:
    tenant: TenantEntity


@dataclass(frozen=True)
class UpdateTenantStatusDTO:
    tenant: TenantEntity
