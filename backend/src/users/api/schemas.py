from pydantic import BaseModel, AnyHttpUrl


class ProfileUpdate(BaseModel):
    name: str | None = None
    picture: AnyHttpUrl | None = None
    receive_updates: bool | None = None
