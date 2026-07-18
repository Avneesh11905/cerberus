from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict
from pydantic.networks import UrlConstraints
from src.modules.auth.authorization.domain.enums import GlobalRole

HttpsUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["https"])]


class ProfileUpdate(BaseModel):
    name: str | None = None
    picture: HttpsUrl | None = None
    receive_updates: bool | None = None


class UserProfileRes(BaseModel):
    id: UUID
    email: str
    role: GlobalRole | None = None
    project_id: UUID | None = None
    name: str | None = None
    picture: str | None = None
    receive_updates: bool
    login_methods: list[str]
    model_config = ConfigDict(from_attributes=True)
