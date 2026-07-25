from pydantic import (
    BaseModel,
)


class ProjectFrontendUrlUpdateReq(BaseModel):
    frontend_url: str | None = None
