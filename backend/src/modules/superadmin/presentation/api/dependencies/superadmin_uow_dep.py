from src.modules.superadmin.infrastructure.database.repositories.superadmin_uow import (
    SQLSuperadminUnitOfWork,
)


async def get_superadmin_uow():
    yield SQLSuperadminUnitOfWork()
