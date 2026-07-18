from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.modules.auth.api.dependencies.security import require_role
from src.modules.auth.domain.entities import UserIdentity
from src.modules.superadmin.api.dependencies import (
    ListTenantsUseCaseDep,
    UpdateTenantStatusUseCaseDep,
    UpdateTenantRoleUseCaseDep,
)
from src.modules.superadmin.api.schemas import (
    PaginatedTenantRes,
    TenantRes,
    TenantRoleUpdateReq,
    TenantStatusUpdateReq,
)
from src.shared.api.dependencies import UnitOfWorkDeps

router = APIRouter()


@router.get("/tenants", response_model=PaginatedTenantRes)
async def list_tenants(
    uow: UnitOfWorkDeps,
    use_case: ListTenantsUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """List all registered tenants (dashboard users) with pagination and search."""
    skip = (page - 1) * size
    async with uow:
        tenants, total = await use_case.execute(
            uow.session, skip=skip, limit=size, search=search
        )
    return PaginatedTenantRes(
        items=[TenantRes.model_validate(t) for t in tenants],
        total=total,
        page=page,
        size=size,
    )


@router.patch("/tenants/{tenant_id}/status", response_model=TenantRes)
async def update_tenant_status(
    tenant_id: UUID,
    req: TenantStatusUpdateReq,
    uow: UnitOfWorkDeps,
    use_case: UpdateTenantStatusUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """Disable or re-enable a tenant account."""
    async with uow:
        tenant = await use_case.execute(uow, tenant_id, req.is_active)
    return tenant


@router.patch("/tenants/{tenant_id}/role", response_model=TenantRes)
async def update_tenant_role(
    tenant_id: UUID,
    req: TenantRoleUpdateReq,
    uow: UnitOfWorkDeps,
    use_case: UpdateTenantRoleUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """Promote or demote a tenant to/from SUPERADMIN."""
    async with uow:
        tenant = await use_case.execute(uow.session, tenant_id, req.role)
    return tenant
