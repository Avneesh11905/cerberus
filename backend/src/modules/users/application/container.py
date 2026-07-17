from src.core.container import app_container
from src.modules.users.application.use_cases import (
    GetProfileUseCase,
    UpdateProfileUseCase,
    DeleteAccountUseCase,
)
from sqlalchemy.ext.asyncio import AsyncSession


class UsersUsecaseContainer:
    def __init__(self):
        self.get_profile_usecase: GetProfileUseCase[AsyncSession] = GetProfileUseCase(
            profile_repository=app_container.user_profile_repo,
            cache=app_container.cache_adapter,
        )
        self.update_profile_usecase: UpdateProfileUseCase[AsyncSession] = (
            UpdateProfileUseCase(
                profile_repository=app_container.user_profile_repo,
                cache=app_container.cache_adapter,
            )
        )
        self.delete_account_usecase: DeleteAccountUseCase[AsyncSession] = (
            DeleteAccountUseCase(
                profile_repository=app_container.user_profile_repo,
                cache=app_container.cache_adapter,
            )
        )


users_usecase_container = UsersUsecaseContainer()
