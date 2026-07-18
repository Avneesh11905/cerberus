from pydantic import BaseModel, field_validator


class _EmailMixin(BaseModel):
    @field_validator("email", mode="before", check_fields=False)
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower() if isinstance(v, str) else v
