from typing import Annotated, Any
from uuid import UUID

from pydantic import HttpUrl, BaseModel, ConfigDict, field_validator
from pydantic.networks import UrlConstraints

HttpsUrl = Annotated[HttpUrl, UrlConstraints(allowed_schemes=["https"])]


class UserProfileRes(BaseModel):
    id: UUID
    email: str
    project_id: UUID | None = None
    name: str | None = None
    picture: str | None = None
    receive_updates: bool
    login_methods: list[str]
    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def extract_email(cls, v: Any) -> str:
        if hasattr(v, "value"):
            return str(v.value)
        return str(v)
