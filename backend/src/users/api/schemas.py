from pydantic import AnyHttpUrl, BaseModel


class ProfileUpdate(BaseModel):
    name: str | None = None
    picture: AnyHttpUrl | None = None
    receive_updates: bool | None = None
