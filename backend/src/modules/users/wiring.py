from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.users.application.ports.users_unit_of_work import UserUoWPort
from src.modules.users.application.use_cases import (
    DeleteAccountUseCase,
    GetProfileUseCase,
    UpdateProfileUseCase,
)
from src.modules.users.presentation.api.dependencies.users_uow_dep import get_user_uow

"""
Module: Users API Dependencies
"""


def get_get_profile_use_case(
    uow: Annotated[UserUoWPort, Depends(get_user_uow)],
) -> GetProfileUseCase:
    return GetProfileUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


def get_update_profile_use_case(
    uow: Annotated[UserUoWPort, Depends(get_user_uow)],
) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


def get_delete_account_use_case(
    uow: Annotated[UserUoWPort, Depends(get_user_uow)],
) -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


GetProfileUseCaseDep = Annotated[GetProfileUseCase, Depends(get_get_profile_use_case)]
UpdateProfileUseCaseDep = Annotated[
    UpdateProfileUseCase, Depends(get_update_profile_use_case)
]
DeleteAccountUseCaseDep = Annotated[
    DeleteAccountUseCase, Depends(get_delete_account_use_case)
]
