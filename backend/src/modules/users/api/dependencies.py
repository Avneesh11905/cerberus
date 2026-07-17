"""
Module: Users API Dependencies
"""

from typing import Annotated

from fastapi import Depends

from src.modules.users.application.use_cases import (
    GetProfileUseCase,
    UpdateProfileUseCase,
    DeleteAccountUseCase,
)
from src.modules.users.application.container import users_usecase_container


def get_get_profile_use_case() -> GetProfileUseCase:
    return users_usecase_container.get_profile_usecase


def get_update_profile_use_case() -> UpdateProfileUseCase:
    return users_usecase_container.update_profile_usecase


def get_delete_account_use_case() -> DeleteAccountUseCase:
    return users_usecase_container.delete_account_usecase


GetProfileUseCaseDep = Annotated[GetProfileUseCase, Depends(get_get_profile_use_case)]
UpdateProfileUseCaseDep = Annotated[
    UpdateProfileUseCase, Depends(get_update_profile_use_case)
]
DeleteAccountUseCaseDep = Annotated[
    DeleteAccountUseCase, Depends(get_delete_account_use_case)
]
