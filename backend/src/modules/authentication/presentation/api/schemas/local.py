from pydantic import BaseModel, EmailStr, Field

from .mixins import _EmailMixin


class RegisterRequest(_EmailMixin):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = None
    turnstile_token: str | None = None


class LoginRequest(_EmailMixin):
    email: EmailStr
    password: str = Field(..., max_length=128)
    turnstile_token: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str | None = Field(default=None, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(_EmailMixin):
    email: EmailStr
    turnstile_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    turnstile_token: str | None = None


class VerifyEmailRequest(_EmailMixin):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    turnstile_token: str | None = None


class RequestNewVerificationEmail(_EmailMixin):
    email: EmailStr
    turnstile_token: str | None = None
