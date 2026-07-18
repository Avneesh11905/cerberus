from typing import Annotated
from fastapi import Depends
from src.modules.projects.application.use_cases import (
    CreateProjectUseCase,
    ListProjectsUseCase,
    GetProjectUseCase,
    DeleteProjectUseCase,
    UpdateOauthUseCase,
    UpdateOriginsUseCase,
    UpdateEnvironmentUseCase,
    UpdateFrontendUrlUseCase,
    UpdateNameUseCase,
    GetProjectPublicCredentialsUseCase,
    RotateApiKeyUseCase,
    RotateJwtSecretUseCase,
    ListProjectUsersUseCase,
    UpdateUserRoleUseCase,
    SetProjectUserActiveStatusUseCase,
    SetTenantUserActiveStatusUseCase,
    GetProjectClaimsUseCase,
    UpdateProjectClaimsUseCase,
    GetUserClaimsUseCase,
    UpdateUserClaimsUseCase,
)
from src.core.container import app_container


def get_create_project_use_case() -> CreateProjectUseCase:
    return CreateProjectUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        api_key_adapter=app_container.api_key_adapter,
        rsa_key_adapter=app_container.rsa_key_adapter,
    )


def get_list_projects_use_case() -> ListProjectsUseCase:
    return ListProjectsUseCase(query_repository=app_container.project_query_repo)


def get_project_use_case() -> GetProjectUseCase:
    return GetProjectUseCase(query_repository=app_container.project_query_repo)


def get_delete_project_use_case() -> DeleteProjectUseCase:
    return DeleteProjectUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
    )


def get_update_oauth_use_case() -> UpdateOauthUseCase:
    return UpdateOauthUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        encryption_adapter=app_container.encryption_adapter,
    )


def get_update_origins_use_case() -> UpdateOriginsUseCase:
    return UpdateOriginsUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
    )


def get_update_environment_use_case() -> UpdateEnvironmentUseCase:
    return UpdateEnvironmentUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
    )


def get_update_frontend_url_use_case() -> UpdateFrontendUrlUseCase:
    return UpdateFrontendUrlUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
    )


def get_update_name_use_case() -> UpdateNameUseCase:
    return UpdateNameUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
    )


def get_project_public_credentials_use_case() -> GetProjectPublicCredentialsUseCase:
    return GetProjectPublicCredentialsUseCase(
        query_repository=app_container.project_query_repo
    )


def get_rotate_api_key_use_case() -> RotateApiKeyUseCase:
    return RotateApiKeyUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        api_key_adapter=app_container.api_key_adapter,
    )


def get_rotate_jwt_secret_use_case() -> RotateJwtSecretUseCase:
    return RotateJwtSecretUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        rsa_key_adapter=app_container.rsa_key_adapter,
    )


def get_list_project_users_use_case() -> ListProjectUsersUseCase:
    return ListProjectUsersUseCase(
        project_query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


def get_update_user_role_use_case() -> UpdateUserRoleUseCase:
    return UpdateUserRoleUseCase(
        project_query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


def get_set_project_user_active_status_use_case() -> SetProjectUserActiveStatusUseCase:
    return SetProjectUserActiveStatusUseCase(
        project_query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


def get_set_tenant_user_active_status_use_case() -> SetTenantUserActiveStatusUseCase:
    return SetTenantUserActiveStatusUseCase(
        project_query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


def get_project_claims_use_case() -> GetProjectClaimsUseCase:
    return GetProjectClaimsUseCase(query_repository=app_container.project_query_repo)


def get_update_project_claims_use_case() -> UpdateProjectClaimsUseCase:
    return UpdateProjectClaimsUseCase(
        query_repository=app_container.project_query_repo,
        command_repository=app_container.project_command_repo,
        cache=app_container.cache_adapter,
    )


def get_get_user_claims_use_case() -> GetUserClaimsUseCase:
    return GetUserClaimsUseCase(
        query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
    )


def get_update_user_claims_use_case() -> UpdateUserClaimsUseCase:
    return UpdateUserClaimsUseCase(
        query_repository=app_container.project_query_repo,
        project_user_repository=app_container.project_user_repo,
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
UpdateUserRoleUseCaseDep = Annotated[
    UpdateUserRoleUseCase, Depends(get_update_user_role_use_case)
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
