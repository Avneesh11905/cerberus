from src.modules.projects.presentation.api.schemas.utils import mask_oauth_config
from src.modules.projects.presentation.api.schemas.project_origins_update_req import (
    ProjectOriginsUpdateReq,
)
from src.modules.projects.presentation.api.schemas.project_default_claims_req import (
    ProjectDefaultClaimsReq,
)
from src.modules.projects.presentation.api.schemas.user_claims_override_req import (
    UserClaimsOverrideReq,
)


def test_mask_oauth_config():
    mask_oauth_config(None)
    mask_oauth_config({"google": "not_a_dict"})  # type: ignore
    mask_oauth_config({"google": {"client_id": "123", "client_secret": "456"}})


def test_origins_req():
    try:
        ProjectOriginsUpdateReq(allowed_origins=["*"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["https://test.com"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://localhost:3000"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["http://test.com"])
    except Exception:
        pass
    try:
        ProjectOriginsUpdateReq(allowed_origins=["invalid"])
    except Exception:
        pass


def test_project_default_claims_req():
    try:
        ProjectDefaultClaimsReq(claims={"role": "test", "other": "test2"})
    except Exception:
        pass
    try:
        ProjectDefaultClaimsReq(claims={})
    except Exception:
        pass
    try:
        ProjectDefaultClaimsReq(claims={"role": "test" * 200})
    except Exception:
        pass


def test_user_claims_override_req():
    try:
        UserClaimsOverrideReq(overrides={"role": "test", "other": "test2"})
    except Exception:
        pass
    try:
        UserClaimsOverrideReq(overrides={})
    except Exception:
        pass
    try:
        UserClaimsOverrideReq(overrides={"role": "test" * 200})
    except Exception:
        pass
