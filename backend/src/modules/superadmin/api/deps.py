"""
Module: Superadmin API Dependencies
"""
from typing import Annotated

from fastapi import Depends

from src.modules.superadmin.application.use_cases.tenant_management import TenantManagementUseCase
from src.modules.superadmin.infrastructure.sql_tenant_repository import SQLTenantRepositoryAdapter
from src.modules.superadmin.infrastructure.sql_system_log_repository import SQLSystemLogRepositoryAdapter

def get_tenant_management_usecase() -> TenantManagementUseCase:
    # We instantiate adapters here. In a true DI setup, we could pull them from the request state 
    # or a global core container if they had heavy initialization (like DB connection pools), 
    # but for simple stateless repositories, instantiating them per request is fine.
    tenant_repo = SQLTenantRepositoryAdapter()
    log_repo = SQLSystemLogRepositoryAdapter()
    return TenantManagementUseCase(tenant_repository=tenant_repo, log_repository=log_repo)

TenantManagementUseCaseDep = Annotated[TenantManagementUseCase, Depends(get_tenant_management_usecase)]
