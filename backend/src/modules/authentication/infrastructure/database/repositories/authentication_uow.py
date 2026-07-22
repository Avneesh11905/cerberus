from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)
from src.modules.authentication.infrastructure.database.repositories.sql_user_command_repository import (
    SQLUserCommandRepositoryAdapter,
)
from src.modules.authentication.infrastructure.database.repositories.sql_user_maintenance_repository import (
    SQLUserMaintenanceRepositoryAdapter,
)
from src.modules.authentication.infrastructure.database.repositories.sql_user_query_repository import (
    SQLUserQueryRepositoryAdapter,
)
from src.modules.projects.infrastructure.database.repositories.project_query_repository import (
    SQLProjectQueryRepositoryAdapter,
)
from src.shared.application.ports.cache import CachePort
from src.shared.application.ports.encryption import EncryptionPort
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


class SQLAuthUnitOfWork(SQLAlchemyUoWAdapter):
    def __init__(
        self,
        encryption_adapter: EncryptionPort,
        cache: CachePort,
        session_factory: Callable[[], AsyncSession] = AsyncSessionLocal,
    ):
        super().__init__(session_factory)
        self.encryption_adapter = encryption_adapter
        self.cache = cache

    async def __aenter__(self):
        await super().__aenter__()
        self.user_query_repo = SQLUserQueryRepositoryAdapter(self.session)
        self.user_command_repo = SQLUserCommandRepositoryAdapter(self.session)
        self.user_maintenance_repo = SQLUserMaintenanceRepositoryAdapter(self.session)
        self.refresh_token_repo = DBRefreshTokenRepositoryAdapter(
            session=self.session,
            lifetime_days=7,  # from get_settings().core get_settings().token, but we can't import easily, or we inject it
            cache=self.cache,
        )
        self.project_key_repo = SQLProjectQueryRepositoryAdapter(
            self.session, self.encryption_adapter
        )
        return self
