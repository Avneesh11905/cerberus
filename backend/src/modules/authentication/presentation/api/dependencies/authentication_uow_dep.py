from src.core.container import app_container
from src.modules.authentication.infrastructure.database.repositories.authentication_uow import (
    SQLAuthUnitOfWork,
)


async def get_auth_uow():
    yield SQLAuthUnitOfWork(
        encryption_adapter=app_container.encryption_adapter,
        cache=app_container.cache_adapter,
    )
