from .utils import RESERVED_CLAIM_KEYS

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class UserClaimsOverrideReq(BaseModel):
    overrides: dict[str, str | int | bool | float] = Field(default_factory=dict)

    @field_validator("overrides")
    @classmethod
    def validate_overrides(cls, v):
        forbidden = set(v.keys()) & RESERVED_CLAIM_KEYS
        if forbidden:
            raise ValueError(f"Reserved keys: {forbidden}")
        return v
