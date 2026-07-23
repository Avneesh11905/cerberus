from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class RegisterResponse(BaseModel):
    message: str
    expires_in_seconds: int
    resend_cooldown_seconds: int | None = None


class LoginResponse(BaseModel):
    message: str
    csrf_token: str
    access_token: str
    user: dict
