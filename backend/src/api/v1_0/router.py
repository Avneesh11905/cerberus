from fastapi import APIRouter

from src.modules.analytics.api.routes import router as analytics_router
from src.modules.auth.api.routes import router as auth_router
from src.modules.projects.api.routes import router as projects_router
from src.modules.superadmin.api.routes import router as superadmin_router
from src.modules.users.api.routes import router as users_router
from src.shared.api.routes.health import router as health_router

api_router = APIRouter(prefix="/v1.0")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(superadmin_router)
api_router.include_router(analytics_router)
