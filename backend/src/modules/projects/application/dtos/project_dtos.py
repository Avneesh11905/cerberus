from dataclasses import dataclass
from collections.abc import Sequence, Mapping
from pydantic import JsonValue

from src.modules.projects.domain.entities import ProjectEntity
from src.modules.projects.domain.entities.project_user import ProjectUser


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
    claims: Mapping[str, JsonValue]


@dataclass(frozen=True)
class GetProjectPublicCredentialsDTO:
    public_key: str
    api_key_hash: str


@dataclass(frozen=True)
class GetUserClaimsDTO:
    claims: Mapping[str, JsonValue]


@dataclass(frozen=True)
class ListProjectsDTO:
    projects: Sequence[ProjectEntity]
    total: int


@dataclass(frozen=True)
class ListProjectUsersDTO:
    users: Sequence[ProjectUser]
    total: int


@dataclass(frozen=True)
class RotateApiKeyDTO:
    api_key_plaintext: str


@dataclass(frozen=True)
class RotateJwtSecretDTO:
    public_pem: str


@dataclass(frozen=True)
class SetProjectUserActiveStatusDTO:
    user: ProjectUser


@dataclass(frozen=True)
class SetTenantUserActiveStatusDTO:
    users: Sequence[ProjectUser]


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
    user: ProjectUser
