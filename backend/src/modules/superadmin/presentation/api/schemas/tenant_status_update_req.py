from pydantic import BaseModel


class TenantStatusUpdateReq(BaseModel):
    is_active: bool
