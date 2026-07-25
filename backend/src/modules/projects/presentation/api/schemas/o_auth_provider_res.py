from pydantic import BaseModel


class OAuthProviderRes(BaseModel):
    key: str
    display_name: str
    scopes: list[str]
    required_fields: list[str]
