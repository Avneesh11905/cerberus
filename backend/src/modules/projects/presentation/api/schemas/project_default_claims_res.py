from pydantic import JsonValue
from collections.abc import Mapping
from uuid import UUID

from pydantic import (
    BaseModel,
)


class ProjectDefaultClaimsRes(BaseModel):
    project_id: UUID
    default_claims: Mapping[str, JsonValue]
