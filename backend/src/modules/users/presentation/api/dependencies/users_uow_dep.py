from src.modules.users.infrastructure.database.repositories.users_uow import (
    SQLUserUnitOfWork,
)


async def get_user_uow():
    yield SQLUserUnitOfWork()
