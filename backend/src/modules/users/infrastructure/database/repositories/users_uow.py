from src.modules.authentication.infrastructure.database.repositories.refresh_token_repository import (
    DBRefreshTokenRepositoryAdapter,
)
from src.modules.users.infrastructure.database.repositories.user_profile_repository import (
    SQLUserProfileRepositoryAdapter,
)
from src.shared.infrastructure.adapters.shared_uow import SQLAlchemyUoWAdapter


class SQLUserUnitOfWork(SQLAlchemyUoWAdapter):
    async def __aenter__(self):
        await super().__aenter__()
        from src.core.config import get_settings
        from src.core.container import app_container

        self.refresh_repo = DBRefreshTokenRepositoryAdapter(
            self.session,
            get_settings().token.REFRESH_TOKEN_LIFETIME_DAYS,
            app_container.cache_adapter,
        )
        self.profile_repo = SQLUserProfileRepositoryAdapter(
            self.session, self.refresh_repo
        )
        return self
