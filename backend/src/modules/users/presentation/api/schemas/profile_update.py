from typing import Annotated

from pydantic import HttpUrl, BaseModel
from pydantic.networks import UrlConstraints

HttpsUrl = Annotated[HttpUrl, UrlConstraints(allowed_schemes=["https"])]


class ProfileUpdate(BaseModel):
    name: str | None = None
    picture: HttpsUrl | None = None
    receive_updates: bool | None = None
