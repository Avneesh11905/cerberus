from pydantic import BaseModel


class OAuthPreflightResponse(BaseModel):
    redirect_url: str


class ExchangeRequest(BaseModel):
    code: str


class ExchangeResponse(BaseModel):
    is_new_user: bool
    csrf_token: str
    access_token: str
    user: dict
    """CSRF token to store in memory on clients that cannot read it from document.cookie
    (i.e. consumers on foreign domains). Must be sent as the X-CSRF header on all
    subsequent state-mutating requests.
    """
