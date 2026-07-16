from fastapi import APIRouter

from src.modules.users.api.routes.profile import router as profile_router

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(profile_router)
