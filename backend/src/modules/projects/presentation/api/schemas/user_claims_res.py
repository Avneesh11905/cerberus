from pydantic import JsonValue
from uuid import UUID

from pydantic import (
    BaseModel,
)


class UserClaimsRes(BaseModel):
    user_id: UUID
    default_claims: dict[str, JsonValue]
    user_overrides: dict[str, JsonValue]
    effective_claims: dict[str, JsonValue]
