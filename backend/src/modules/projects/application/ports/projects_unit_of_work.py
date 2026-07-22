from typing import Protocol

from src.modules.projects.application.ports.project_command_repository import (
    ProjectCommandRepositoryPort,
)
from src.modules.projects.application.ports.project_query_repository import (
    ProjectQueryRepositoryPort,
)
from src.modules.projects.application.ports.project_user_repository import (
    ProjectUserRepositoryPort,
)


class ProjectUoWPort[SessionType](Protocol):
    @property
    def session(self) -> SessionType: ...
    @property
    def project_query_repo(self) -> ProjectQueryRepositoryPort: ...
    @property
    def project_command_repo(self) -> ProjectCommandRepositoryPort: ...
    @property
    def project_user_repo(self) -> ProjectUserRepositoryPort: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, traceback): ...
