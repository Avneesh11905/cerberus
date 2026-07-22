from src.core.container import app_container
from src.modules.projects.infrastructure.database.repositories.projects_uow import (
    SQLProjectUnitOfWork,
)


async def get_project_uow():
    yield SQLProjectUnitOfWork(encryption_adapter=app_container.encryption_adapter)
