from src.core.container import app_container
from src.modules.superadmin.application.use_cases import (
    GetSystemAnalyticsUseCase,
    ListTenantsUseCase,
    UpdateTenantStatusUseCase,
    UpdateTenantRoleUseCase,
    ListTenantLogsUseCase,
)
from sqlalchemy.ext.asyncio import AsyncSession


class SuperadminUsecaseContainer:
    def __init__(self):
        self.get_system_analytics_usecase: GetSystemAnalyticsUseCase[AsyncSession] = (
            GetSystemAnalyticsUseCase(
                analytics_repository=app_container.superadmin_analytics_repo
            )
        )
        self.list_tenants_usecase: ListTenantsUseCase[AsyncSession] = (
            ListTenantsUseCase(tenant_repository=app_container.superadmin_tenant_repo)
        )
        self.update_tenant_status_usecase: UpdateTenantStatusUseCase[AsyncSession] = (
            UpdateTenantStatusUseCase(
                tenant_repository=app_container.superadmin_tenant_repo,
                refresh_repo=app_container.refresh_token_repo,
                cache=app_container.cache_adapter,
            )
        )
        self.update_tenant_role_usecase: UpdateTenantRoleUseCase[AsyncSession] = (
            UpdateTenantRoleUseCase(
                tenant_repository=app_container.superadmin_tenant_repo
            )
        )
        self.list_tenant_logs_usecase: ListTenantLogsUseCase[AsyncSession] = (
            ListTenantLogsUseCase(log_repository=app_container.superadmin_log_repo)
        )


superadmin_usecase_container = SuperadminUsecaseContainer()
