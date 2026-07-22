from src.modules.analytics.infrastructure.database.repositories.repository import (
    SQLAnalyticsRepositoryAdapter,
)
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


class SQLAnalyticsUnitOfWork(SQLAlchemyUoWAdapter):
    async def __aenter__(self):
        await super().__aenter__()
        self.analytics_repo = SQLAnalyticsRepositoryAdapter(self.session)
        return self
