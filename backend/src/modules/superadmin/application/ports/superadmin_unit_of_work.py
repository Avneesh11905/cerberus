from typing import Protocol

from src.modules.authentication.application.ports.repository.refresh_token import (
    RefreshTokenRepositoryPort,
)
from src.modules.superadmin.application.ports.system_analytics_repository import (
    SystemAnalyticsRepositoryPort,
)
from src.modules.superadmin.application.ports.system_log_repository import (
    SystemLogRepositoryPort,
)
from src.modules.superadmin.application.ports.tenant_repository import (
    TenantRepositoryPort,
)


class SuperAdminUoWPort[SessionType](Protocol):
    @property
    def session(self) -> SessionType: ...
    @property
    def tenant_repo(self) -> TenantRepositoryPort: ...
    @property
    def refresh_token_repo(self) -> RefreshTokenRepositoryPort: ...
    @property
    def log_repo(self) -> SystemLogRepositoryPort: ...
    @property
    def analytics_repo(self) -> SystemAnalyticsRepositoryPort: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, traceback): ...
