from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.modules.projects.infrastructure.database.repositories.project_command_repository import (
    SQLProjectCommandRepositoryAdapter,
)
from src.modules.projects.infrastructure.database.repositories.project_query_repository import (
    SQLProjectQueryRepositoryAdapter,
)
from src.modules.projects.infrastructure.database.repositories.project_user_repository import (
    SQLProjectUserRepositoryAdapter,
)
from src.shared.application.ports.encryption import EncryptionPort
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


class SQLProjectUnitOfWork(SQLAlchemyUoWAdapter):
    def __init__(
        self,
        encryption_adapter: EncryptionPort,
        session_factory: Callable[[], AsyncSession] = AsyncSessionLocal,
    ):
        super().__init__(session_factory)
        self.encryption_adapter = encryption_adapter

    async def __aenter__(self):
        await super().__aenter__()
        self.project_query_repo = SQLProjectQueryRepositoryAdapter(
            self.session, self.encryption_adapter
        )
        self.project_command_repo = SQLProjectCommandRepositoryAdapter(
            self.session, self.encryption_adapter
        )
        self.project_user_repo = SQLProjectUserRepositoryAdapter(self.session)
        return self
