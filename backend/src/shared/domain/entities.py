from pydantic import BaseModel


class ClientMetadata(BaseModel):
    """Metadata about the client making the request (e.g., extracted from HTTP headers)."""

    ip_address: str | None = None
    user_agent: str | None = None
    extra_headers: dict[str, str] | None = None
