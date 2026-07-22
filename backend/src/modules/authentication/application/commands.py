from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.shared.domain.entities import ClientMetadata


@dataclass(frozen=True)
class LocalRegisterCommand:
    email: str
    password: str
    name: Optional[str] = None
    project_id: Optional[UUID] = None
    client_meta: Optional[ClientMetadata] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class LocalLoginCommand:
    email: str
    password: str
    client_meta: Optional[ClientMetadata] = None
    project_id: Optional[UUID] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class LocalVerifyEmailCommand:
    email: str
    otp: str
    client_meta: Optional[ClientMetadata] = None
    project_id: Optional[UUID] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class LocalResendVerificationCommand:
    email: str
    project_id: Optional[UUID] = None
    client_meta: Optional[ClientMetadata] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class PasswordResetRequestCommand:
    email: str
    project_id: Optional[UUID] = None
    client_meta: Optional[ClientMetadata] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class PasswordResetExecuteCommand:
    token: str
    new_password: str
    client_meta: Optional[ClientMetadata] = None
    is_challenged: bool = False
    turnstile_token: Optional[str] = None


@dataclass(frozen=True)
class PasswordChangeCommand:
    user_id: UUID
    new_password: str
    current_password: Optional[str] = None


@dataclass(frozen=True)
class SessionLogoutCommand:
    refresh_token: Optional[str] = None
    jti: Optional[str] = None
    exp: Optional[int] = None


@dataclass(frozen=True)
class SessionLogoutAllCommand:
    user_id: UUID
    jti: Optional[str] = None
    exp: Optional[int] = None


@dataclass(frozen=True)
class SessionRefreshCommand:
    refresh_token: str
    client_meta: Optional[ClientMetadata] = None


@dataclass(frozen=True)
class SessionRevokeCommand:
    user_id: UUID
    family_id: UUID


@dataclass(frozen=True)
class TenantOAuthLoginUrlQuery[RequestType]:
    request: RequestType
    provider: str
    redirect_uri: str


@dataclass(frozen=True)
class TenantOAuthCallbackCommand[RequestType]:
    provider: str
    request: RequestType
    client_meta: Optional[ClientMetadata] = None


@dataclass(frozen=True)
class ProjectUserOAuthLoginUrlQuery[RequestType]:
    request: RequestType
    provider: str
    redirect_uri: str
    project_id: Optional[UUID] = None
    request_origin: Optional[str] = None


@dataclass(frozen=True)
class ProjectUserOAuthCallbackCommand[RequestType]:
    provider: str
    project_id: UUID
    request: RequestType
    client_meta: Optional[ClientMetadata] = None


@dataclass(frozen=True)
class OAuthExchangeCommand:
    code: str


@dataclass(frozen=True)
class ListActiveSessionsQuery:
    user_id: UUID
    current_token: Optional[str] = None
