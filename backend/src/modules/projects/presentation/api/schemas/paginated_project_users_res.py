from src.modules.users.presentation.api.schemas.user_profile_res import UserProfileRes

from pydantic import (
    BaseModel,
)


class PaginatedProjectUsersRes(BaseModel):
    items: list[UserProfileRes]
    total: int
    page: int
    size: int
