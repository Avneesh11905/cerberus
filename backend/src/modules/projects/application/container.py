from src.core.container import app_container
from sqlalchemy.ext.asyncio import AsyncSession
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
    GetSecretsUseCase,
    RotateApiKeyUseCase,
    RotateJwtSecretUseCase,
    ListProjectUsersUseCase,
    UpdateUserRoleUseCase,
    ToggleUserStatusUseCase,
    ToggleTenantUserStatusUseCase,
)


class ProjectsUsecaseContainer:
    def __init__(self):
        self.create_project_usecase: CreateProjectUseCase[AsyncSession] = (
            CreateProjectUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
                api_key_adapter=app_container.api_key_adapter,
                rsa_key_adapter=app_container.rsa_key_adapter,
            )
        )
        self.list_projects_usecase: ListProjectsUseCase[AsyncSession] = (
            ListProjectsUseCase(query_repository=app_container.project_query_repo)
        )
        self.get_project_usecase: GetProjectUseCase[AsyncSession] = GetProjectUseCase(
            query_repository=app_container.project_query_repo
        )
        self.delete_project_usecase: DeleteProjectUseCase[AsyncSession] = (
            DeleteProjectUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
            )
        )
        self.update_oauth_usecase: UpdateOauthUseCase[AsyncSession] = (
            UpdateOauthUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
                encryption_adapter=app_container.encryption_adapter,
            )
        )
        self.update_origins_usecase: UpdateOriginsUseCase[AsyncSession] = (
            UpdateOriginsUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
            )
        )
        self.update_environment_usecase: UpdateEnvironmentUseCase[AsyncSession] = (
            UpdateEnvironmentUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
            )
        )
        self.update_frontend_url_usecase: UpdateFrontendUrlUseCase[AsyncSession] = (
            UpdateFrontendUrlUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
            )
        )
        self.update_name_usecase: UpdateNameUseCase[AsyncSession] = UpdateNameUseCase(
            query_repository=app_container.project_query_repo,
            command_repository=app_container.project_command_repo,
        )
        self.get_secrets_usecase: GetSecretsUseCase[AsyncSession] = GetSecretsUseCase(
            query_repository=app_container.project_query_repo
        )
        self.rotate_api_key_usecase: RotateApiKeyUseCase[AsyncSession] = (
            RotateApiKeyUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
                api_key_adapter=app_container.api_key_adapter,
            )
        )
        self.rotate_jwt_secret_usecase: RotateJwtSecretUseCase[AsyncSession] = (
            RotateJwtSecretUseCase(
                query_repository=app_container.project_query_repo,
                command_repository=app_container.project_command_repo,
                rsa_key_adapter=app_container.rsa_key_adapter,
            )
        )
        self.list_project_users_usecase: ListProjectUsersUseCase[AsyncSession] = (
            ListProjectUsersUseCase(
                project_query_repository=app_container.project_query_repo,
                project_user_repository=app_container.project_user_repo,
            )
        )
        self.update_user_role_usecase: UpdateUserRoleUseCase[AsyncSession] = (
            UpdateUserRoleUseCase(
                project_query_repository=app_container.project_query_repo,
                project_user_repository=app_container.project_user_repo,
            )
        )
        self.toggle_user_status_usecase: ToggleUserStatusUseCase[AsyncSession] = (
            ToggleUserStatusUseCase(
                project_query_repository=app_container.project_query_repo,
                project_user_repository=app_container.project_user_repo,
            )
        )
        self.toggle_tenant_user_status_usecase: ToggleTenantUserStatusUseCase[
            AsyncSession
        ] = ToggleTenantUserStatusUseCase(
            project_query_repository=app_container.project_query_repo,
            project_user_repository=app_container.project_user_repo,
        )


projects_usecase_container = ProjectsUsecaseContainer()
