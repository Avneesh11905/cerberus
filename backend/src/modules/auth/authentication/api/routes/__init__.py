from fastapi import APIRouter

from src.modules.auth.authentication.api.routes.local import router as local_router
from src.modules.auth.authentication.api.routes.oauth import router as oauth_router
from src.modules.auth.authentication.api.routes.password import (
    router as password_router,
)
from src.modules.auth.authentication.api.routes.session import (
    router as session_router,
)
from src.modules.auth.authentication.api.routes.verification import (
    router as verification_router,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
router.include_router(local_router)
router.include_router(session_router)
router.include_router(oauth_router)
router.include_router(password_router)
router.include_router(verification_router)
