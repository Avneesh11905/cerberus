import pytest
from httpx import AsyncClient


# Patch the dev_enabled dependency check via fixture or we can patch get_settings().core directly
@pytest.fixture
def mock_dev_env(mocker):
    from src.core.config import get_settings

    mocker.patch.object(get_settings().core, "ENV", "development")


@pytest.mark.asyncio
async def test_debug_email_gallery(client: AsyncClient, mock_dev_env):
    response = await client.get("/dev/email/preview/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Gallery" in response.text or "<html" in response.text


@pytest.mark.asyncio
async def test_debug_email_specific_template(client: AsyncClient, mock_dev_env):
    response = await client.get("/dev/email/preview/onboarding/welcome.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Demo User" in response.text


@pytest.mark.asyncio
async def test_debug_email_invalid_path(client: AsyncClient, mock_dev_env):
    # Test path traversal prevention
    response = await client.get("/dev/email/preview/..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid template path"


@pytest.mark.asyncio
async def test_debug_email_not_found(client: AsyncClient, mock_dev_env):
    response = await client.get("/dev/email/preview/nonexistent/template.html")
    assert response.status_code == 404
    assert response.json()["detail"] == "Template not found"


@pytest.mark.asyncio
async def test_debug_email_production_disabled(client: AsyncClient, mocker):
    from src.core.config import get_settings

    mocker.patch.object(get_settings().core, "ENV", "production")

    response = await client.get("/dev/email/preview/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Dev routes disabled"
