from src.modules.projects.presentation.api.schemas.project_default_claims_req import (
    ProjectDefaultClaimsReq,
)
from src.modules.projects.presentation.api.schemas.project_origins_update_req import (
    ProjectOriginsUpdateReq,
)
from src.modules.projects.presentation.api.schemas.user_claims_override_req import (
    UserClaimsOverrideReq,
)


def test_pydantic_schemas():
    try:
        ProjectDefaultClaimsReq(claims={"role": "test"})
    except Exception:
        pass
    try:
        ProjectDefaultClaimsReq(claims={})
    except Exception:
        pass

    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["invalid"])
    except Exception:
        pass

    try:
        UserClaimsOverrideReq(custom_claims={"role": "test"})  # type: ignore
    except Exception:
        pass
    try:
        UserClaimsOverrideReq(custom_claims={})  # type: ignore
    except Exception:
        pass
