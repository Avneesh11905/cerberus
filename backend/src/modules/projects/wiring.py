from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.projects.application.ports.projects_unit_of_work import ProjectUoWPort
from src.modules.projects.application.use_cases import (
    CreateProjectUseCase,
    DeleteProjectUseCase,
    GetProjectClaimsUseCase,
    GetProjectPublicCredentialsUseCase,
    GetProjectUseCase,
    GetUserClaimsUseCase,
    ListProjectsUseCase,
    ListProjectUsersUseCase,
    ListTenantUsersUseCase,
    RotateApiKeyUseCase,
    RotateJwtSecretUseCase,
    SetProjectUserActiveStatusUseCase,
    SetTenantUserActiveStatusUseCase,
    UpdateEnvironmentUseCase,
    UpdateFrontendUrlUseCase,
    UpdateNameUseCase,
    UpdateOauthUseCase,
    UpdateOriginsUseCase,
    UpdateProjectClaimsUseCase,
    UpdateUserClaimsUseCase,
)
from src.modules.projects.presentation.api.dependencies.projects_uow_dep import (
    get_project_uow,
)


def get_create_project_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> CreateProjectUseCase:
    return CreateProjectUseCase(
        uow=uow,
        api_key_adapter=app_container.api_key_adapter,
        rsa_key_adapter=app_container.rsa_key_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_list_projects_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> ListProjectsUseCase:
    return ListProjectsUseCase(uow=uow)


def get_project_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> GetProjectUseCase:
    return GetProjectUseCase(uow=uow)


def get_delete_project_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(uow=uow)


def get_update_oauth_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateOauthUseCase:
    return UpdateOauthUseCase(
        uow=uow,
        encryption_adapter=app_container.encryption_adapter,
    )


def get_update_origins_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateOriginsUseCase:
    return UpdateOriginsUseCase(uow=uow)


def get_update_environment_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateEnvironmentUseCase:
    return UpdateEnvironmentUseCase(uow=uow)


def get_update_frontend_url_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateFrontendUrlUseCase:
    return UpdateFrontendUrlUseCase(uow=uow)


def get_update_name_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateNameUseCase:
    return UpdateNameUseCase(uow=uow)


def get_project_public_credentials_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> GetProjectPublicCredentialsUseCase:
    return GetProjectPublicCredentialsUseCase(uow=uow)


def get_rotate_api_key_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> RotateApiKeyUseCase:
    return RotateApiKeyUseCase(
        uow=uow,
        api_key_adapter=app_container.api_key_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_rotate_jwt_secret_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> RotateJwtSecretUseCase:
    return RotateJwtSecretUseCase(
        uow=uow,
        rsa_key_adapter=app_container.rsa_key_adapter,
        analytics=app_container.analytics_adapter,
    )


def get_list_project_users_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> ListProjectUsersUseCase:
    return ListProjectUsersUseCase(uow=uow)


def get_list_tenant_users_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> ListTenantUsersUseCase:
    return ListTenantUsersUseCase(uow=uow)


def get_set_project_user_active_status_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> SetProjectUserActiveStatusUseCase:
    return SetProjectUserActiveStatusUseCase(uow=uow)


def get_set_tenant_user_active_status_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> SetTenantUserActiveStatusUseCase:
    return SetTenantUserActiveStatusUseCase(uow=uow)


def get_project_claims_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> GetProjectClaimsUseCase:
    return GetProjectClaimsUseCase(uow=uow)


def get_update_project_claims_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateProjectClaimsUseCase:
    return UpdateProjectClaimsUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


def get_get_user_claims_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> GetUserClaimsUseCase:
    return GetUserClaimsUseCase(uow=uow)


def get_update_user_claims_use_case(
    uow: Annotated[ProjectUoWPort, Depends(get_project_uow)],
) -> UpdateUserClaimsUseCase:
    return UpdateUserClaimsUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


CreateProjectUseCaseDep = Annotated[
    CreateProjectUseCase, Depends(get_create_project_use_case)
]
ListProjectsUseCaseDep = Annotated[
    ListProjectsUseCase, Depends(get_list_projects_use_case)
]
GetProjectUseCaseDep = Annotated[GetProjectUseCase, Depends(get_project_use_case)]
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
GetProjectPublicCredentialsUseCaseDep = Annotated[
    GetProjectPublicCredentialsUseCase, Depends(get_project_public_credentials_use_case)
]
RotateApiKeyUseCaseDep = Annotated[
    RotateApiKeyUseCase, Depends(get_rotate_api_key_use_case)
]
RotateJwtSecretUseCaseDep = Annotated[
    RotateJwtSecretUseCase, Depends(get_rotate_jwt_secret_use_case)
]

ListProjectUsersUseCaseDep = Annotated[
    ListProjectUsersUseCase, Depends(get_list_project_users_use_case)
]

ListTenantUsersUseCaseDep = Annotated[
    ListTenantUsersUseCase, Depends(get_list_tenant_users_use_case)
]

SetProjectUserActiveStatusUseCaseDep = Annotated[
    SetProjectUserActiveStatusUseCase,
    Depends(get_set_project_user_active_status_use_case),
]
SetTenantUserActiveStatusUseCaseDep = Annotated[
    SetTenantUserActiveStatusUseCase,
    Depends(get_set_tenant_user_active_status_use_case),
]
GetProjectClaimsUseCaseDep = Annotated[
    GetProjectClaimsUseCase, Depends(get_project_claims_use_case)
]
UpdateProjectClaimsUseCaseDep = Annotated[
    UpdateProjectClaimsUseCase, Depends(get_update_project_claims_use_case)
]
GetUserClaimsUseCaseDep = Annotated[
    GetUserClaimsUseCase, Depends(get_get_user_claims_use_case)
]
UpdateUserClaimsUseCaseDep = Annotated[
    UpdateUserClaimsUseCase, Depends(get_update_user_claims_use_case)
]
