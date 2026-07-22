from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.superadmin.application.ports.superadmin_unit_of_work import (
    SuperAdminUoWPort,
)
from src.modules.superadmin.application.use_cases import (
    GetSystemAnalyticsUseCase,
    ListTenantLogsUseCase,
    ListTenantsUseCase,
    UpdateTenantGlobalRoleUseCase,
    UpdateTenantStatusUseCase,
)
from src.modules.superadmin.presentation.api.dependencies.superadmin_uow_dep import (
    get_superadmin_uow,
)

"""
Module: Superadmin API Dependencies
"""


def get_get_system_analytics_use_case(
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
) -> GetSystemAnalyticsUseCase:
    return GetSystemAnalyticsUseCase(uow=uow)


def get_list_tenants_use_case(
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
) -> ListTenantsUseCase:
    return ListTenantsUseCase(uow=uow)


def get_update_tenant_status_use_case(
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
) -> UpdateTenantStatusUseCase:
    return UpdateTenantStatusUseCase(
        uow=uow,
        cache=app_container.cache_adapter,
    )


def get_update_tenant_global_role_use_case(
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
) -> UpdateTenantGlobalRoleUseCase:
    return UpdateTenantGlobalRoleUseCase(uow=uow)


def get_list_tenant_logs_use_case(
    uow: Annotated[SuperAdminUoWPort, Depends(get_superadmin_uow)],
) -> ListTenantLogsUseCase:
    return ListTenantLogsUseCase(uow=uow)


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
