"""
Module: Superadmin API Dependencies
"""

from typing import Annotated

from fastapi import Depends
from src.core.container import app_container
from src.modules.superadmin.application.use_cases import (
    GetSystemAnalyticsUseCase,
    ListTenantsUseCase,
    UpdateTenantStatusUseCase,
    UpdateTenantGlobalRoleUseCase,
    ListTenantLogsUseCase,
)


def get_get_system_analytics_use_case() -> GetSystemAnalyticsUseCase:
    return GetSystemAnalyticsUseCase(
        analytics_repository=app_container.superadmin_analytics_repo
    )


def get_list_tenants_use_case() -> ListTenantsUseCase:
    return ListTenantsUseCase(tenant_repository=app_container.superadmin_tenant_repo)


def get_update_tenant_status_use_case() -> UpdateTenantStatusUseCase:
    return UpdateTenantStatusUseCase(
        tenant_repository=app_container.superadmin_tenant_repo,
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
    )


def get_update_tenant_global_role_use_case() -> UpdateTenantGlobalRoleUseCase:
    return UpdateTenantGlobalRoleUseCase(
        tenant_repository=app_container.superadmin_tenant_repo
    )


def get_list_tenant_logs_use_case() -> ListTenantLogsUseCase:
    return ListTenantLogsUseCase(log_repository=app_container.superadmin_log_repo)


GetSystemAnalyticsUseCaseDep = Annotated[
    GetSystemAnalyticsUseCase, Depends(get_get_system_analytics_use_case)
]
ListTenantsUseCaseDep = Annotated[
    ListTenantsUseCase, Depends(get_list_tenants_use_case)
]
UpdateTenantStatusUseCaseDep = Annotated[
    UpdateTenantStatusUseCase, Depends(get_update_tenant_status_use_case)
]
UpdateTenantGlobalRoleUseCaseDep = Annotated[
    UpdateTenantGlobalRoleUseCase, Depends(get_update_tenant_global_role_use_case)
]
ListTenantLogsUseCaseDep = Annotated[
    ListTenantLogsUseCase, Depends(get_list_tenant_logs_use_case)
]
