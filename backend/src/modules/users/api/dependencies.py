"""
Module: Users API Dependencies
"""

from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.users.application.use_cases.profile_management import (
    ProfileManagementUseCase,
)


def get_profile_management_usecase() -> ProfileManagementUseCase:
    return ProfileManagementUseCase(
        profile_repository=app_container.user_profile_repo,
        cache=app_container.cache_adapter,
    )


ProfileManagementUseCaseDep = Annotated[
    ProfileManagementUseCase, Depends(get_profile_management_usecase)
]
