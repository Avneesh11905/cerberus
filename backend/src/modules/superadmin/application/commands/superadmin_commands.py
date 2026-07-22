from dataclasses import dataclass
from uuid import UUID

from src.modules.authorization.domain.enums import GlobalRole


@dataclass(frozen=True)
class UpdateTenantGlobalRoleCommand:
    tenant_id: UUID
    role: GlobalRole


@dataclass(frozen=True)
class UpdateTenantStatusCommand:
    tenant_id: UUID
    is_active: bool
