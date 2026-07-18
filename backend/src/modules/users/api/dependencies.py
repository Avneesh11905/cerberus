"""
Module: Users API Dependencies
"""

from typing import Annotated

from fastapi import Depends
from src.core.container import app_container
from src.modules.users.application.use_cases import (
    GetProfileUseCase,
    UpdateProfileUseCase,
    DeleteAccountUseCase,
)


def get_get_profile_use_case() -> GetProfileUseCase:
    return GetProfileUseCase(
        profile_repository=app_container.user_profile_repo,
        cache=app_container.cache_adapter,
    )


def get_update_profile_use_case() -> UpdateProfileUseCase:
    return UpdateProfileUseCase(
        profile_repository=app_container.user_profile_repo,
        cache=app_container.cache_adapter,
    )


def get_delete_account_use_case() -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        profile_repository=app_container.user_profile_repo,
        cache=app_container.cache_adapter,
    )


GetProfileUseCaseDep = Annotated[GetProfileUseCase, Depends(get_get_profile_use_case)]
UpdateProfileUseCaseDep = Annotated[
    UpdateProfileUseCase, Depends(get_update_profile_use_case)
]
DeleteAccountUseCaseDep = Annotated[
    DeleteAccountUseCase, Depends(get_delete_account_use_case)
]
