from fastapi import APIRouter

from src.modules.analytics.presentation.api.routes.projects import (
    router as projects_router,
)
from src.modules.analytics.presentation.api.routes.tenants import (
    router as tenants_router,
)
from src.modules.analytics.presentation.api.routes.project_events import (
    router as project_events_router,
)
from src.modules.analytics.presentation.api.routes.tenant_events import (
    router as tenant_events_router,
)
from src.modules.analytics.presentation.api.routes.system_events import (
    router as system_events_router,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])
router.include_router(projects_router)
router.include_router(tenants_router)
router.include_router(project_events_router)
router.include_router(tenant_events_router)
router.include_router(system_events_router)
