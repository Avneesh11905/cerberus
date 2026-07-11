from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.modules.auth.api.dependencies import require_role
from src.modules.auth.domain import UserIdentity
from src.modules.superadmin.api.deps import TenantManagementUseCaseDep
from src.modules.superadmin.api.schemas import SystemLogRes, TenantRes, TenantStatusUpdateReq, TenantRoleUpdateReq
from src.modules.superadmin.domain.exceptions import TenantNotFoundException
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter(prefix="/superadmin", tags=["Superadmin"])


@router.get("/tenants", response_model=list[TenantRes])
async def list_tenants(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """List all registered tenants (dashboard users)."""
    async with uow:
        tenants = await use_case.list_tenants(uow.session)
    return tenants


@router.patch("/tenants/{tenant_id}/status", response_model=TenantRes)
async def update_tenant_status(
    tenant_id: UUID,
    req: TenantStatusUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """Disable or re-enable a tenant account."""
    async with uow:
        try:
            tenant = await use_case.update_status(
                uow.session, tenant_id, req.is_active
            )
        except TenantNotFoundException:
            raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/tenants/{tenant_id}/role", response_model=TenantRes)
async def update_tenant_role(
    tenant_id: UUID,
    req: TenantRoleUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
):
    """Promote or demote a tenant to/from SUPERADMIN."""
    async with uow:
        try:
            tenant = await use_case.update_role(
                uow.session, tenant_id, req.role
            )
        except TenantNotFoundException:
            raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("/logs", response_model=list[SystemLogRes])
async def list_system_logs(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    use_case: TenantManagementUseCaseDep,
    admin: Annotated[UserIdentity, Depends(require_role("SUPERADMIN"))],
    limit: int = 100,
):
    """View recent system activity logs (audits, errors, events)."""
    async with uow:
        logs = await use_case.list_logs(uow.session, limit=limit)
    return logs
