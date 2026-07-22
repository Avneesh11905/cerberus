from typing import Protocol

from src.modules.users.application.ports.user_profile_repository import (
    UserProfileRepositoryPort,
)


class UserUoWPort[SessionType](Protocol):
    @property
    def session(self) -> SessionType: ...
    @property
    def profile_repo(self) -> UserProfileRepositoryPort: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, traceback): ...
