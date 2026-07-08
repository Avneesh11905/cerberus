from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select

from src.admin.schemas import SystemLogRes, TenantRes, TenantStatusUpdateReq
from src.authentication.api.dependencies import require_role
from src.authentication.container import get_container
from src.authentication.core.domain import UserIdentity
from src.shared.config import token_settings
from src.shared.infrastructure.sql.tables import SystemLog, User
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("/tenants", response_model=list[TenantRes])
async def list_tenants(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    admin: Annotated[UserIdentity, Depends(require_role("admin"))],
):
    """List all tenants in the system."""
    async with uow:
        result = await uow.session.execute(
            select(User).where(User.role == "tenant")
        )
        tenants = result.scalars().all()
    return tenants


@admin_router.patch("/tenants/{tenant_id}/status", response_model=TenantRes)
async def update_tenant_status(
    tenant_id: UUID,
    req: TenantStatusUpdateReq,
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    admin: Annotated[UserIdentity, Depends(require_role("admin"))],
):
    """Enable or disable a tenant (preventing them from logging in if disabled)."""
    async with uow:
        result = await uow.session.execute(
            select(User).where(User.id == tenant_id, User.role == "tenant")
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant.is_active = req.is_active
        await uow.session.flush()

        if not req.is_active:
            container = get_container()
            await container.refresh_token_repo.revoke_all_for_user(uow.session, tenant.id)
            #  TTL must match refresh token lifetime so the flag persists across refresh.
            # Previously 900 (15 min) let a disabled tenant regain access after waiting.
            await container.cache_adapter.set_string(
                f"disabled_user:{tenant.id}", "1",
                ttl=token_settings.REFRESH_TOKEN_LIFETIME_DAYS * 86400
            )
            # INFO-2: Removed explicit commit — UoW __aexit__ handles it; double-commit is redundant.
        await uow.session.refresh(tenant)

    return tenant


@admin_router.get("/logs", response_model=list[SystemLogRes])
async def list_system_logs(
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
    admin: Annotated[UserIdentity, Depends(require_role("admin"))],
    limit: int = Query(50, le=200, description="Max records per page"),
    offset: int = Query(0, ge=0, description="Number of records to skip (cursor)"),
    level: str | None = None,
    source: str | None = None,
):
    """Fetch paginated system logs (server-side). true backend pagination."""
    async with uow:
        stmt = select(SystemLog).order_by(desc(SystemLog.created_at))
        
        if level:
            stmt = stmt.where(SystemLog.level == level)
        if source:
            stmt = stmt.where(SystemLog.source == source)
        
        #  offset/limit applied in SQL — no more fetching 500 rows client-side.
        stmt = stmt.offset(offset).limit(limit)
        
        result = await uow.session.execute(stmt)
        logs = result.scalars().all()

    return logs
