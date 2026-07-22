import pytest

from src.core.config.app import URLSettings
from src.core.config.security import SecuritySettings


def test_url_settings_validation():
    # Valid
    s = URLSettings(FRONTEND_URL="http://test.com")
    assert s.FRONTEND_URL == "http://test.com"


def test_security_settings_loads_keys(tmp_path):
    priv = tmp_path / "priv.pem"
    pub = tmp_path / "pub.pem"
    priv.write_text("priv_content")
    pub.write_text("pub_content")

    s = SecuritySettings(
        SESSION_SECRET="0" * 64,
        ENCRYPTION_KEY="0" * 64,
        JWT_PRIVATE_KEY_PATH=str(priv),
        JWT_PUBLIC_KEY_PATH=str(pub),
    )
    assert s.JWT_PRIVATE_KEY == "priv_content"
    assert s.JWT_PUBLIC_KEY == "pub_content"


def test_security_settings_missing_keys(tmp_path):
    with pytest.raises(ValueError, match="file not found"):
        SecuritySettings(
            SESSION_SECRET="0" * 64,
            ENCRYPTION_KEY="0" * 64,
            JWT_PRIVATE_KEY_PATH=str(tmp_path / "missing.pem"),
            JWT_PUBLIC_KEY_PATH=str(tmp_path / "pub.pem"),
        )

    with pytest.raises(ValueError, match="file not found"):
        priv = tmp_path / "priv.pem"
        priv.write_text("priv_content")
        SecuritySettings(
            SESSION_SECRET="0" * 64,
            ENCRYPTION_KEY="0" * 64,
            JWT_PRIVATE_KEY_PATH=str(priv),
            JWT_PUBLIC_KEY_PATH=str(tmp_path / "missing.pem"),
        )
