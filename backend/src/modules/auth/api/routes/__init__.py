from fastapi import APIRouter

from src.modules.auth.api.routes.login import router as login_router
from src.modules.auth.api.routes.oauth import router as oauth_router
from src.modules.auth.api.routes.password import router as password_router
from src.modules.auth.api.routes.register import router as register_router
from src.modules.auth.api.routes.sessions import router as sessions_router
from src.modules.auth.api.routes.verify import router as verify_router

router = APIRouter()
router.include_router(login_router)
router.include_router(oauth_router)
router.include_router(register_router)
router.include_router(verify_router)
router.include_router(password_router)
router.include_router(sessions_router)
