from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.entities import ClientMetadata


@dataclass(frozen=True)
class LocalRegisterCommand:
    email: str
    password: str
    name: str | None = None
    project_id: UUID | None = None
    client_meta: ClientMetadata | None = None
    is_challenged: bool = False
    turnstile_token: str | None = None


@dataclass(frozen=True)
class LocalLoginCommand:
    email: str
    password: str
    client_meta: ClientMetadata | None = None
    project_id: UUID | None = None
    is_challenged: bool = False
    turnstile_token: str | None = None


@dataclass(frozen=True)
class LocalVerifyEmailCommand:
    email: str
    otp: str
    client_meta: ClientMetadata | None = None
    project_id: UUID | None = None
    is_challenged: bool = False


@dataclass(frozen=True)
class LocalResendVerificationCommand:
    email: str
    project_id: UUID | None = None
    client_meta: ClientMetadata | None = None
    is_challenged: bool = False
    turnstile_token: str | None = None


@dataclass(frozen=True)
class PasswordResetRequestCommand:
    email: str
    project_id: UUID | None = None
    client_meta: ClientMetadata | None = None
    is_challenged: bool = False
    turnstile_token: str | None = None


@dataclass(frozen=True)
class PasswordResetExecuteCommand:
    token: str
    new_password: str
    client_meta: ClientMetadata | None = None
    is_challenged: bool = False
    turnstile_token: str | None = None


@dataclass(frozen=True)
class PasswordChangeCommand:
    user_id: UUID
    new_password: str
    current_password: str | None = None


@dataclass(frozen=True)
class SessionLogoutCommand:
    refresh_token: str | None = None
    jti: str | None = None
    exp: int | None = None


@dataclass(frozen=True)
class SessionLogoutAllCommand:
    user_id: UUID
    jti: str | None = None
    exp: int | None = None


@dataclass(frozen=True)
class SessionRefreshCommand:
    refresh_token: str
    client_meta: ClientMetadata | None = None


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
    client_meta: ClientMetadata | None = None


@dataclass(frozen=True)
class ProjectUserOAuthLoginUrlQuery[RequestType]:
    request: RequestType
    provider: str
    redirect_uri: str
    project_id: UUID | None = None
    request_origin: str | None = None


@dataclass(frozen=True)
class ProjectUserOAuthCallbackCommand[RequestType]:
    provider: str
    project_id: UUID
    request: RequestType
    client_meta: ClientMetadata | None = None


@dataclass(frozen=True)
class OAuthExchangeCommand:
    code: str


@dataclass(frozen=True)
class ListActiveSessionsQuery:
    user_id: UUID
    current_token: str | None = None
