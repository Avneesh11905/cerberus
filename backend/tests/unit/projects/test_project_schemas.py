import pytest
from pydantic import ValidationError
from src.modules.projects.presentation.api.schemas.project_origins_update_req import (
    ProjectOriginsUpdateReq,
    mask_oauth_config,
)
from src.modules.projects.presentation.api.schemas.project_default_claims_req import (
    ProjectDefaultClaimsReq,
    mask_oauth_config as mask_oauth_config_2,
)


def test_mask_oauth_config_empty():
    assert mask_oauth_config(None) == {}
    assert mask_oauth_config({}) == {}


def test_mask_oauth_config_masking():
    config = {
        "google": {"client_id": "google_id", "client_secret": "google_secret"},
        "github": {"client_id": "github_id"},
        "invalid_provider": "not_a_dict",
    }

    masked = mask_oauth_config(config)

    assert masked["invalid_provider"] == "not_a_dict"

    assert "client_secret" not in masked["google"]
    assert masked["google"]["client_secret_configured"] is True
    assert masked["google"]["client_id"] == "google_id"

    assert "client_secret" not in masked["github"]
    assert masked["github"]["client_secret_configured"] is False
    assert masked["github"]["client_id"] == "github_id"

    # Original config shouldn't be mutated
    assert "client_secret" in config["google"]


def test_project_origins_update_req_valid():
    req = ProjectOriginsUpdateReq(
        allowed_origins=["https://example.com", "http://localhost:3000", "*"]
    )
    assert len(req.allowed_origins) == 3


def test_project_origins_update_req_invalid_scheme():
    with pytest.raises(ValidationError):
        ProjectOriginsUpdateReq(allowed_origins=["ftp://example.com"])


def test_project_origins_update_req_invalid_http_not_localhost():
    with pytest.raises(ValidationError):
        ProjectOriginsUpdateReq(allowed_origins=["http://example.com"])


def test_project_origins_update_req_invalid_url():
    with pytest.raises(ValidationError):
        ProjectOriginsUpdateReq(allowed_origins=["not_a_url"])


def test_mask_oauth_config_2():
    assert mask_oauth_config_2(None) == {}


def test_project_default_claims_req_valid():
    req = ProjectDefaultClaimsReq(claims={"is_admin": True})
    assert req.claims["is_admin"] is True


def test_project_default_claims_req_too_many():
    claims = {f"key_{i}": True for i in range(11)}
    with pytest.raises(ValidationError):
        ProjectDefaultClaimsReq(claims=claims)  # type: ignore


def test_project_default_claims_req_reserved():
    with pytest.raises(ValidationError):
        ProjectDefaultClaimsReq(claims={"sub": "test"})


def test_project_default_claims_req_invalid_identifier():
    with pytest.raises(ValidationError):
        ProjectDefaultClaimsReq(claims={"invalid-key": "test"})
