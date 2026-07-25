from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.authorization.domain.enums import GlobalRole
from src.shared.domain.value_objects import EmailAddress, PersonName


@dataclass(kw_only=True)
class TenantEntity:
    id: UUID
    email: EmailAddress
    name: PersonName | None
    is_active: bool
    role: GlobalRole
    created_at: datetime
