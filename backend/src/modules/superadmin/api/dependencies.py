"""
Module: Superadmin API Dependencies
"""

from typing import Annotated

from fastapi import Depends

from src.modules.superadmin.application.use_cases.get_system_analytics import (
    GetSystemAnalyticsUseCase,
)
from src.modules.superadmin.application.use_cases.list_tenants import ListTenantsUseCase
from src.modules.superadmin.application.use_cases.update_tenant_status import (
    UpdateTenantStatusUseCase,
)
from src.modules.superadmin.application.use_cases.update_tenant_role import (
    UpdateTenantRoleUseCase,
)
from src.modules.superadmin.application.use_cases.list_tenant_logs import (
    ListTenantLogsUseCase,
)
from src.modules.superadmin.application.container import superadmin_usecase_container


def get_get_system_analytics_use_case() -> GetSystemAnalyticsUseCase:
    return superadmin_usecase_container.get_system_analytics_usecase


def get_list_tenants_use_case() -> ListTenantsUseCase:
    return superadmin_usecase_container.list_tenants_usecase


def get_update_tenant_status_use_case() -> UpdateTenantStatusUseCase:
    return superadmin_usecase_container.update_tenant_status_usecase


def get_update_tenant_role_use_case() -> UpdateTenantRoleUseCase:
    return superadmin_usecase_container.update_tenant_role_usecase


def get_list_tenant_logs_use_case() -> ListTenantLogsUseCase:
    return superadmin_usecase_container.list_tenant_logs_usecase


GetSystemAnalyticsUseCaseDep = Annotated[
    GetSystemAnalyticsUseCase, Depends(get_get_system_analytics_use_case)
]
ListTenantsUseCaseDep = Annotated[
    ListTenantsUseCase, Depends(get_list_tenants_use_case)
]
UpdateTenantStatusUseCaseDep = Annotated[
    UpdateTenantStatusUseCase, Depends(get_update_tenant_status_use_case)
]
UpdateTenantRoleUseCaseDep = Annotated[
    UpdateTenantRoleUseCase, Depends(get_update_tenant_role_use_case)
]
ListTenantLogsUseCaseDep = Annotated[
    ListTenantLogsUseCase, Depends(get_list_tenant_logs_use_case)
]
