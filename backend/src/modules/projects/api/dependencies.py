"""
Module: Projects Dependencies
"""

from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.projects.application.use_cases.project_management import (
    ProjectManagementUseCase,
)
from src.modules.projects.application.use_cases.project_user_management import (
    ProjectUserManagementUseCase,
)


def get_project_management_usecase() -> ProjectManagementUseCase:
    return ProjectManagementUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        encryption_adapter=app_container.encryption_adapter,
        api_key_adapter=app_container.api_key_adapter,
        rsa_key_adapter=app_container.rsa_key_adapter,
    )


ProjectManagementUseCaseDep = Annotated[
    ProjectManagementUseCase, Depends(get_project_management_usecase)
]


def get_project_user_management_usecase() -> ProjectUserManagementUseCase:
    return ProjectUserManagementUseCase(
        project_query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


ProjectUserManagementUseCaseDep = Annotated[
    ProjectUserManagementUseCase, Depends(get_project_user_management_usecase)
]
