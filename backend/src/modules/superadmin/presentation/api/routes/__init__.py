from fastapi import APIRouter

from .system import router as system_router
from .tenants import router as tenants_router

router = APIRouter(prefix="/superadmin", tags=["Superadmin"])

router.include_router(tenants_router)
router.include_router(system_router)
