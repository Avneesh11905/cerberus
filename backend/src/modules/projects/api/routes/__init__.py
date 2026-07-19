from fastapi import APIRouter

from .keys import router as keys_router
from .projects import router as projects_router
from .settings import router as settings_router
from .users import router as users_router
from .server import router as server_router

router = APIRouter(prefix="/projects", tags=["Projects"])

router.include_router(projects_router)
router.include_router(settings_router)
router.include_router(keys_router)
router.include_router(server_router)
router.include_router(users_router)
