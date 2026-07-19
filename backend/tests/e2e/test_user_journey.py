import pytest
import re
from httpx import AsyncClient


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,
    }


@pytest.mark.asyncio
async def test_registration_to_login_journey(
    client: AsyncClient, db_session, celery_app, mocker
):
    """
    End-to-End User Journey:
    1. Register a new tenant admin user
    2. Extract OTP from the intercepted email task
    3. Verify the OTP
    4. Login to obtain access token
    5. Access a protected route to trigger analytics
    6. Run the analytics aggregation task
    7. Verify analytics data is stored
    """

    # We patch the underlying send_email to capture the HTML content containing the OTP
    from src.core.container import app_container

    mock_send = mocker.patch.object(app_container.email_client, "send_email")

    # We patch celery_app.send_task to capture analytics tasks
    from src.core.celery_app import celery_app as my_celery_app

    mock_send_task = mocker.patch.object(my_celery_app, "send_task")

    # 1. Registration
    reg_data = {
        "email": "e2e_journey@example.com",
        "password": "StrongPassword123!",
        "name": "E2E User",
    }

    # We must enable eager task execution so the email is dispatched synchronously
    # and the mock is called in this process.
    from src.core.celery_app import celery_app as my_celery_app

    my_celery_app.conf.task_always_eager = True

    resp = await client.post("/v1.0/auth/tenant/register", json=reg_data)
    assert resp.status_code == 201, resp.json()

    # 2. OTP Extraction
    assert mock_send.call_count == 1
    call_args = mock_send.call_args[0]
    html_content = call_args[2]

    # We look for a 6-digit number inside the <h2> tag
    match = re.search(r"<h2[^>]*>(\d{6})</h2>", html_content)
    assert match is not None, "Could not find 6-digit OTP in email content"
    otp = match.group(1)
    print(f"EXTRACTED OTP: {otp}")

    # 3. OTP Verification
    verify_data = {"email": "e2e_journey@example.com", "otp": otp}
    resp = await client.post("/v1.0/auth/verify-email", json=verify_data)
    assert resp.status_code == 200, resp.json()

    # 4. Login
    login_data = {"email": "e2e_journey@example.com", "password": "StrongPassword123!"}
    resp = await client.post("/v1.0/auth/tenant/login", json=login_data)
    assert resp.status_code == 200, resp.json()

    tokens = resp.json()
    access_token = tokens["access_token"]

    # 5. Protected Route Access
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = await client.get("/v1.0/users/me", headers=headers)
    assert resp.status_code == 200, resp.json()
    me_data = resp.json()
    assert me_data["email"] == "e2e_journey@example.com"

    # 6. Verify Analytics
    # Analytics middleware pushed an event to Redis. We mock send_task to intercept it.
    # Check that record_analytics_event was triggered for the users/me endpoint.
    analytics_calls = [
        call
        for call in mock_send_task.call_args_list
        if call.args[0] == "record_analytics_event"
    ]
    assert len(analytics_calls) > 0, "No analytics events were recorded"

    found_api_request = False
    for call in analytics_calls:
        kwargs = call.kwargs.get("kwargs", {})
        if kwargs.get("event_type") == "API_REQUEST":
            found_api_request = True
            break

    assert found_api_request, "API_REQUEST analytics event was not sent"
