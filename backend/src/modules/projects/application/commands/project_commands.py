from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass(frozen=True)
class CreateProjectCommand:
    user_id: UUID
    name: str


@dataclass(frozen=True)
class DeleteProjectCommand:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class RotateApiKeyCommand:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class RotateJwtSecretCommand:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class SetProjectUserActiveStatusCommand:
    project_id: UUID
    tenant_id: Optional[UUID]
    user_id: UUID
    is_active: bool


@dataclass(frozen=True)
class SetTenantUserActiveStatusCommand:
    tenant_id: UUID
    email: str
    is_active: bool


@dataclass(frozen=True)
class UpdateEnvironmentCommand:
    project_id: UUID
    user_id: UUID
    environment: str


@dataclass(frozen=True)
class UpdateFrontendUrlCommand:
    project_id: UUID
    user_id: UUID
    frontend_url: Optional[str]


@dataclass(frozen=True)
class UpdateNameCommand:
    project_id: UUID
    user_id: UUID
    name: str


@dataclass(frozen=True)
class UpdateOauthCommand:
    project_id: UUID
    user_id: UUID
    incoming_config: Dict[str, Any]


@dataclass(frozen=True)
class UpdateOriginsCommand:
    project_id: UUID
    user_id: UUID
    allowed_origins: List[str]


@dataclass(frozen=True)
class UpdateProjectClaimsCommand:
    project_id: UUID
    user_id: UUID
    default_claims: Dict[str, Any]


@dataclass(frozen=True)
class UpdateUserClaimsCommand:
    project_id: UUID
    tenant_id: Optional[UUID]
    user_id: UUID
    overrides: Dict[str, Any]
