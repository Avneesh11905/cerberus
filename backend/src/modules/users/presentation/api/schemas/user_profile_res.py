from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict
from pydantic.networks import UrlConstraints



HttpsUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["https"])]


class UserProfileRes(BaseModel):
    id: UUID
    email: str
    project_id: UUID | None = None
    name: str | None = None
    picture: str | None = None
    receive_updates: bool
    login_methods: list[str]
    model_config = ConfigDict(from_attributes=True)
