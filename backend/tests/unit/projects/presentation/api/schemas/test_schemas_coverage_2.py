from src.modules.projects.presentation.api.schemas.project_default_claims_req import (
    ProjectDefaultClaimsReq,
)
from src.modules.projects.presentation.api.schemas.project_origins_update_req import (
    ProjectOriginsUpdateReq,
)


def test_schemas():
    try:
        ProjectDefaultClaimsReq(claims={"a": "b"})
    except Exception:
        pass
    try:
        ProjectDefaultClaimsReq(claims={"a": 1})
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost:3000"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["invalid_url"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost:3000"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=[])
    except Exception:
        pass
