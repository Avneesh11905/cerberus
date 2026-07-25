from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID


class MessageResponse(BaseModel):
    message: str


class RegisterResponse(BaseModel):
    message: str
    expires_in_seconds: int
    resend_cooldown_seconds: int | None = None


class UserIdentityRes(BaseModel):
    id: UUID
    email: str
    name: str | None = None
    picture: str | None = None
    role: str | None = None
    is_verified: bool
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", "picture", mode="before")
    @classmethod
    def extract_value(cls, v: object) -> str | None:
        if hasattr(v, "value"):
            val = getattr(v, "value")
            return str(val) if val is not None else None
        return v if v is None else str(v)


class LoginResponse(BaseModel):
    message: str
    csrf_token: str
    access_token: str
    user: UserIdentityRes


class RefreshResponse(BaseModel):
    access_token: str
    csrf_token: str
    user: UserIdentityRes
