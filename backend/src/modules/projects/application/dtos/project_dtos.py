from dataclasses import dataclass
from typing import Any, Dict, Sequence

from src.modules.projects.domain.entities import ProjectEntity
from src.modules.users.domain.entities import UserProfile


@dataclass(frozen=True)
class CreateProjectDTO:
    project: ProjectEntity
    api_key_plaintext: str
    public_pem: str


@dataclass(frozen=True)
class GetProjectDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class GetProjectClaimsDTO:
    claims: Dict[str, Any]


@dataclass(frozen=True)
class GetProjectPublicCredentialsDTO:
    public_key: str
    api_key_hash: str


@dataclass(frozen=True)
class GetUserClaimsDTO:
    claims: Dict[str, Any]


@dataclass(frozen=True)
class ListProjectsDTO:
    projects: Sequence[ProjectEntity]


@dataclass(frozen=True)
class ListProjectUsersDTO:
    users: Sequence[UserProfile]
    total: int


@dataclass(frozen=True)
class RotateApiKeyDTO:
    api_key_plaintext: str


@dataclass(frozen=True)
class RotateJwtSecretDTO:
    public_pem: str


@dataclass(frozen=True)
class SetProjectUserActiveStatusDTO:
    user: UserProfile


@dataclass(frozen=True)
class SetTenantUserActiveStatusDTO:
    users: Sequence[UserProfile]


@dataclass(frozen=True)
class UpdateEnvironmentDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateFrontendUrlDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateNameDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateOauthDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateOriginsDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateProjectClaimsDTO:
    project: ProjectEntity


@dataclass(frozen=True)
class UpdateUserClaimsDTO:
    user: UserProfile
