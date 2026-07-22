from typing import Protocol

from src.modules.authentication.application.ports.repository.project_key_repository import (
    ProjectKeyRepositoryPort,
)
from src.modules.authentication.application.ports.repository.refresh_token import (
    RefreshTokenRepositoryPort,
)
from src.modules.authentication.application.ports.repository.user_command_repository import (
    UserCommandRepositoryPort,
)
from src.modules.authentication.application.ports.repository.user_maintenance_repository import (
    UserMaintenanceRepositoryPort,
)
from src.modules.authentication.application.ports.repository.user_query_repository import (
    UserQueryRepositoryPort,
)
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)


class AuthUoWPort[SessionType](Protocol):
    @property
    def session(self) -> SessionType: ...
    @property
    def user_query_repo(self) -> UserQueryRepositoryPort: ...
    @property
    def user_command_repo(self) -> UserCommandRepositoryPort: ...
    @property
    def user_maintenance_repo(self) -> UserMaintenanceRepositoryPort: ...
    @property
    def refresh_token_repo(self) -> RefreshTokenRepositoryPort: ...
    @property
    def project_key_repo(self) -> ProjectKeyRepositoryPort: ...
    @property
    def project_query_repo(self) -> ProjectQueryRepositoryPort: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, traceback): ...
