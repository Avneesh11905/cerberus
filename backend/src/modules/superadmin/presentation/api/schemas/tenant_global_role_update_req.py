from pydantic import BaseModel

from src.modules.authorization.domain.enums import GlobalRole


class TenantGlobalRoleUpdateReq(BaseModel):
    role: GlobalRole
