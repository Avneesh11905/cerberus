from fastapi import APIRouter

from src.modules.analytics.presentation.api.routes.projects import (
    router as projects_router,
)
from src.modules.analytics.presentation.api.routes.tenants import (
    router as tenants_router,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
router.include_router(projects_router)
router.include_router(tenants_router)
