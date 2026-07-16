from typing import Annotated

from pydantic import AnyUrl, BaseModel
from pydantic.networks import UrlConstraints

HttpsUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["https"])]


class ProfileUpdate(BaseModel):
    name: str | None = None
    picture: HttpsUrl | None = None
    receive_updates: bool | None = None


class UserProfileRes(BaseModel):
    id: str
    email: str
    role: str
    project_id: str | None = None
    name: str | None = None
    picture: str | None = None
    receive_updates: bool
    login_methods: list[str]
