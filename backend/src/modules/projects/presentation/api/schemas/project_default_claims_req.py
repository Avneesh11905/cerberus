from .utils import RESERVED_CLAIM_KEYS

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


from pydantic import JsonValue


class ProjectDefaultClaimsReq(BaseModel):
    claims: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("claims")
    @classmethod
    def validate_claims(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 claim keys")
        forbidden = set(v.keys()) & RESERVED_CLAIM_KEYS
        if forbidden:
            raise ValueError(f"Reserved keys: {forbidden}")
        for key in v:
            if not key.isidentifier():
                raise ValueError(f"Invalid key name: '{key}'")
        return v
