from fastapi import APIRouter

from src.modules.analytics.presentation.api.routes import router as analytics_router
from src.modules.authentication.presentation.api.routes import (
    router as auth_router,
)
from src.modules.projects.presentation.api.routes import router as projects_router
from src.modules.superadmin.presentation.api.routes import router as superadmin_router
from src.modules.users.presentation.api.routes import router as users_router


api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(projects_router)
api_router.include_router(superadmin_router)
api_router.include_router(analytics_router)
