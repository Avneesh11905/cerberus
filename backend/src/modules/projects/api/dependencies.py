from typing import Annotated

from fastapi import Depends

from src.modules.projects.application.use_cases.create_project import (
    CreateProjectUseCase,
)
from src.modules.projects.application.use_cases.list_projects import ListProjectsUseCase
from src.modules.projects.application.use_cases.get_project import GetProjectUseCase
from src.modules.projects.application.use_cases.delete_project import (
    DeleteProjectUseCase,
)
from src.modules.projects.application.use_cases.update_oauth import UpdateOauthUseCase
from src.modules.projects.application.use_cases.update_origins import (
    UpdateOriginsUseCase,
)
from src.modules.projects.application.use_cases.update_environment import (
    UpdateEnvironmentUseCase,
)
from src.modules.projects.application.use_cases.update_frontend_url import (
    UpdateFrontendUrlUseCase,
)
from src.modules.projects.application.use_cases.update_name import UpdateNameUseCase
from src.modules.projects.application.use_cases.get_secrets import GetSecretsUseCase
from src.modules.projects.application.use_cases.rotate_api_key import (
    RotateApiKeyUseCase,
)
from src.modules.projects.application.use_cases.rotate_jwt_secret import (
    RotateJwtSecretUseCase,
)

from src.modules.projects.application.use_cases.list_project_users import (
    ListProjectUsersUseCase,
)
from src.modules.projects.application.use_cases.update_user_role import (
    UpdateUserRoleUseCase,
)
from src.modules.projects.application.use_cases.toggle_user_status import (
    ToggleUserStatusUseCase,
)
from src.modules.projects.application.use_cases.toggle_tenant_user_status import (
    ToggleTenantUserStatusUseCase,
)

from src.modules.projects.application.container import projects_usecase_container


def get_create_project_use_case() -> CreateProjectUseCase:
    return projects_usecase_container.create_project_usecase


def get_list_projects_use_case() -> ListProjectsUseCase:
    return projects_usecase_container.list_projects_usecase


def get_get_project_use_case() -> GetProjectUseCase:
    return projects_usecase_container.get_project_usecase


def get_delete_project_use_case() -> DeleteProjectUseCase:
    return projects_usecase_container.delete_project_usecase


def get_update_oauth_use_case() -> UpdateOauthUseCase:
    return projects_usecase_container.update_oauth_usecase


def get_update_origins_use_case() -> UpdateOriginsUseCase:
    return projects_usecase_container.update_origins_usecase


def get_update_environment_use_case() -> UpdateEnvironmentUseCase:
    return projects_usecase_container.update_environment_usecase


def get_update_frontend_url_use_case() -> UpdateFrontendUrlUseCase:
    return projects_usecase_container.update_frontend_url_usecase


def get_update_name_use_case() -> UpdateNameUseCase:
    return projects_usecase_container.update_name_usecase


def get_get_secrets_use_case() -> GetSecretsUseCase:
    return projects_usecase_container.get_secrets_usecase


def get_rotate_api_key_use_case() -> RotateApiKeyUseCase:
    return projects_usecase_container.rotate_api_key_usecase


def get_rotate_jwt_secret_use_case() -> RotateJwtSecretUseCase:
    return projects_usecase_container.rotate_jwt_secret_usecase


def get_list_project_users_use_case() -> ListProjectUsersUseCase:
    return projects_usecase_container.list_project_users_usecase


def get_update_user_role_use_case() -> UpdateUserRoleUseCase:
    return projects_usecase_container.update_user_role_usecase


def get_toggle_user_status_use_case() -> ToggleUserStatusUseCase:
    return projects_usecase_container.toggle_user_status_usecase


def get_toggle_tenant_user_status_use_case() -> ToggleTenantUserStatusUseCase:
    return projects_usecase_container.toggle_tenant_user_status_usecase


CreateProjectUseCaseDep = Annotated[
    CreateProjectUseCase, Depends(get_create_project_use_case)
]
ListProjectsUseCaseDep = Annotated[
    ListProjectsUseCase, Depends(get_list_projects_use_case)
]
GetProjectUseCaseDep = Annotated[GetProjectUseCase, Depends(get_get_project_use_case)]
DeleteProjectUseCaseDep = Annotated[
    DeleteProjectUseCase, Depends(get_delete_project_use_case)
]
UpdateOauthUseCaseDep = Annotated[
    UpdateOauthUseCase, Depends(get_update_oauth_use_case)
]
UpdateOriginsUseCaseDep = Annotated[
    UpdateOriginsUseCase, Depends(get_update_origins_use_case)
]
UpdateEnvironmentUseCaseDep = Annotated[
    UpdateEnvironmentUseCase, Depends(get_update_environment_use_case)
]
UpdateFrontendUrlUseCaseDep = Annotated[
    UpdateFrontendUrlUseCase, Depends(get_update_frontend_url_use_case)
]
UpdateNameUseCaseDep = Annotated[UpdateNameUseCase, Depends(get_update_name_use_case)]
GetSecretsUseCaseDep = Annotated[GetSecretsUseCase, Depends(get_get_secrets_use_case)]
RotateApiKeyUseCaseDep = Annotated[
    RotateApiKeyUseCase, Depends(get_rotate_api_key_use_case)
]
RotateJwtSecretUseCaseDep = Annotated[
    RotateJwtSecretUseCase, Depends(get_rotate_jwt_secret_use_case)
]

ListProjectUsersUseCaseDep = Annotated[
    ListProjectUsersUseCase, Depends(get_list_project_users_use_case)
]
UpdateUserRoleUseCaseDep = Annotated[
    UpdateUserRoleUseCase, Depends(get_update_user_role_use_case)
]
ToggleUserStatusUseCaseDep = Annotated[
    ToggleUserStatusUseCase, Depends(get_toggle_user_status_use_case)
]
ToggleTenantUserStatusUseCaseDep = Annotated[
    ToggleTenantUserStatusUseCase, Depends(get_toggle_tenant_user_status_use_case)
]
