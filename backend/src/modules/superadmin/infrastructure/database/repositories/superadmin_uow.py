from src.modules.superadmin.infrastructure.database.repositories.system_analytics_repository import (
    SQLSystemAnalyticsRepositoryAdapter,
)
from src.modules.superadmin.infrastructure.database.repositories.system_log_repository import (
    SQLSystemLogRepositoryAdapter,
)
from src.modules.superadmin.infrastructure.database.repositories.tenant_repository import (
    SQLTenantRepositoryAdapter,
)
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


class SQLSuperadminUnitOfWork(SQLAlchemyUoWAdapter):
    async def __aenter__(self):
        await super().__aenter__()
        self.tenant_repo = SQLTenantRepositoryAdapter(self.session)
        self.log_repo = SQLSystemLogRepositoryAdapter(self.session)
        self.analytics_repo = SQLSystemAnalyticsRepositoryAdapter(self.session)
        return self
