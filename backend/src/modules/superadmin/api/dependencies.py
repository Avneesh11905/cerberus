"""
Module: Superadmin API Dependencies
"""

from typing import Annotated

from fastapi import Depends

from src.core.container import app_container
from src.modules.superadmin.application.use_cases.tenant_management import (
    TenantManagementUseCase,
)


def get_tenant_management_usecase() -> TenantManagementUseCase:
    return TenantManagementUseCase(
        tenant_repository=app_container.superadmin_tenant_repo,
        log_repository=app_container.superadmin_log_repo,
        analytics_repository=app_container.superadmin_analytics_repo,
        refresh_repo=app_container.refresh_token_repo,
        cache=app_container.cache_adapter,
    )


TenantManagementUseCaseDep = Annotated[
    TenantManagementUseCase, Depends(get_tenant_management_usecase)
]
