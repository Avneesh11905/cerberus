from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetProjectQuery:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class GetProjectClaimsQuery:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class GetProjectPublicCredentialsQuery:
    project_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class GetUserClaimsQuery:
    project_id: UUID
    tenant_id: UUID | None
    user_id: UUID


@dataclass(frozen=True)
class ListProjectsQuery:
    user_id: UUID


@dataclass(frozen=True)
class ListProjectUsersQuery:
    project_id: UUID
    tenant_id: UUID | None
    skip: int = 0
    limit: int = 20
    search: str | None = None
