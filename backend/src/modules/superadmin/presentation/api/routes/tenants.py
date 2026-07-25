from uuid import UUID

from fastapi import APIRouter

from src.modules.authorization.presentation.api.dependencies.roles import (
    RequireSuperAdminRoleDep,
)
from src.modules.superadmin.application.commands.superadmin_commands import (
    UpdateTenantGlobalRoleCommand,
    UpdateTenantStatusCommand,
)
from src.modules.superadmin.presentation.api.schemas import (
    PaginatedTenantRes,
    TenantGlobalRoleUpdateReq,
    TenantRes,
    TenantStatusUpdateReq,
)
from src.modules.superadmin.wiring import (
    ListTenantsUseCaseDep,
    UpdateTenantGlobalRoleUseCaseDep,
    UpdateTenantStatusUseCaseDep,
)

router = APIRouter()


@router.get("/tenants", response_model=PaginatedTenantRes)
async def list_tenants(
    use_case: ListTenantsUseCaseDep,
    admin: RequireSuperAdminRoleDep,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
):
    """List all registered tenants (dashboard users) with pagination and search."""
    skip = (page - 1) * size
    tenants, total = await use_case.execute(skip=skip, limit=size, search=search)
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
    use_case: UpdateTenantStatusUseCaseDep,
    admin: RequireSuperAdminRoleDep,
):
    """Disable or re-enable a tenant account."""
    if tenant_id == admin.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="You cannot modify your own status")
    dto = await use_case.execute(
        UpdateTenantStatusCommand(tenant_id=tenant_id, is_active=req.is_active)
    )
    tenant = dto.tenant
    return tenant


@router.patch("/tenants/{tenant_id}/role", response_model=TenantRes)
async def update_tenant_global_role(
    tenant_id: UUID,
    req: TenantGlobalRoleUpdateReq,
    use_case: UpdateTenantGlobalRoleUseCaseDep,
    admin: RequireSuperAdminRoleDep,
):
    """Promote or demote a tenant to/from SUPERADMIN."""
    if tenant_id == admin.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="You cannot modify your own role")
    dto = await use_case.execute(
        UpdateTenantGlobalRoleCommand(tenant_id=tenant_id, role=req.role)
    )
    tenant = dto.tenant
    return tenant
