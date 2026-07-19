import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

from src.shared.adapters.email_client import (
    SMTPEmailClientAdapter,
    ResendEmailClientAdapter,
)
from src.modules.auth.authentication.adapters.email_sender import AuthEmailSenderAdapter


@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.error = AsyncMock()
    return logger


@pytest.fixture
def mock_task_runner():
    runner = MagicMock()
    runner.add_task = MagicMock()
    return runner


@pytest.fixture
def mock_email_client():
    client = MagicMock()
    client.send_email = MagicMock()
    return client


@pytest.fixture
def templates_dir():
    # The templates should be loaded from src/shared/templates/emails
    base_dir = (
        Path(__file__).parent.parent.parent.parent
        / "src"
        / "shared"
        / "templates"
        / "emails"
    )
    return base_dir


def test_smtp_email_client_adapter(mocker):
    smtp_mock = mocker.patch("src.shared.adapters.email_client.smtplib.SMTP")
    server_mock = MagicMock()
    smtp_mock.return_value.__enter__.return_value = server_mock

    adapter = SMTPEmailClientAdapter(
        smtp_host="localhost",
        smtp_port=1025,
        from_email="test@cerberus.local",
        reply_to="reply@cerberus.local",
    )

    adapter.send_email(to="user@example.com", subject="Test", html="<p>Hi</p>")

    smtp_mock.assert_called_once_with("localhost", 1025)
    server_mock.send_message.assert_called_once()
    msg = server_mock.send_message.call_args[0][0]
    assert msg["Subject"] == "Test"
    assert msg["From"] == "test@cerberus.local"
    assert msg["To"] == "user@example.com"
    assert msg["Reply-To"] == "reply@cerberus.local"


def test_resend_email_client_adapter(mocker):
    resend_mock = mocker.patch("src.shared.adapters.email_client.resend.Emails.send")

    adapter = ResendEmailClientAdapter(
        api_key="re_test123",
        from_email="test@cerberus.local",
        reply_to="reply@cerberus.local",
    )

    adapter.send_email(to="user@example.com", subject="Test", html="<p>Hi</p>")

    resend_mock.assert_called_once_with(
        {
            "from": "test@cerberus.local",
            "to": ["user@example.com"],
            "subject": "Test",
            "html": "<p>Hi</p>",
            "reply_to": "reply@cerberus.local",
        }
    )


@pytest.mark.asyncio
async def test_auth_email_sender_welcome(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    from src.modules.auth.authentication.infrastructure.tasks import dispatch_email_task

    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    await sender.send_welcome_email(to_email="user@example.com", name="Alice")

    mock_task_runner.add_task.assert_called_once()
    args, kwargs = mock_task_runner.add_task.call_args
    assert args[0] == dispatch_email_task
    assert kwargs["to_email"] == "user@example.com"
    assert kwargs["subject"] == "Welcome to Cerberus!"
    assert "Alice" in kwargs["html_content"]
    assert "Cerberus" in kwargs["html_content"]
    assert "http://localhost:3000/" in kwargs["html_content"]


@pytest.mark.asyncio
async def test_auth_email_sender_welcome_no_name(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    await sender.send_welcome_email(to_email="user@example.com", name=None)
    kwargs = mock_task_runner.add_task.call_args.kwargs
    assert "there" in kwargs["html_content"]  # fallback for missing name


@pytest.mark.asyncio
async def test_auth_email_sender_password_reset(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    reset_url = "http://localhost:3000/reset?token=123"
    await sender.send_password_reset_email(
        to_email="user@example.com", reset_url=reset_url
    )

    kwargs = mock_task_runner.add_task.call_args.kwargs
    assert kwargs["subject"] == "Password Reset - Cerberus"
    assert reset_url in kwargs["html_content"]


@pytest.mark.asyncio
async def test_auth_email_sender_verification(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    await sender.send_verification_email(to_email="user@example.com", otp="123456")

    kwargs = mock_task_runner.add_task.call_args.kwargs
    assert kwargs["subject"] == "Verify your Email - Cerberus"
    assert "123456" in kwargs["html_content"]


@pytest.mark.asyncio
async def test_auth_email_sender_account_restored(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    await sender.send_account_restored_email(to_email="user@example.com", name="Bob")

    kwargs = mock_task_runner.add_task.call_args.kwargs
    assert kwargs["subject"] == "Security Alert: Your Cerberus account was restored"
    assert "Bob" in kwargs["html_content"]


@pytest.mark.asyncio
async def test_auth_email_sender_login_detected(
    mock_email_client, mock_logger, mock_task_runner, templates_dir, mocker
):
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="modern",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    await sender.send_login_detected_email(
        to_email="user@example.com", ip_address="192.168.1.1", device_info="MacBook Pro"
    )

    kwargs = mock_task_runner.add_task.call_args.kwargs
    assert kwargs["subject"] == "New Login Detected - Cerberus"
    assert "192.168.1.1" in kwargs["html_content"]
    assert "MacBook Pro" in kwargs["html_content"]


@pytest.mark.asyncio
async def test_auth_email_sender_render_error(
    mock_email_client, mock_logger, mock_task_runner, templates_dir
):
    # This tests the exception block inside _render_and_dispatch
    sender = AuthEmailSenderAdapter(
        email_client=mock_email_client,
        from_email="noreply@cerberus.local",
        templates_dir=templates_dir,
        logger=mock_logger,
        proj_name="Cerberus",
        template_name="light",
        frontend_url="http://localhost:3000",
        task_runner=mock_task_runner,
    )

    # Induce an error by passing a template name that doesn't exist
    await sender._render_and_dispatch(
        to_email="user@example.com",
        subject="Fail",
        template_name="nonexistent.html",
        context={},
    )

    # Logger should have captured the TemplateNotFound error
    mock_task_runner.add_task.assert_not_called()
    mock_logger.error.assert_called_once()
    assert "Failed to dispatch email 'Fail'" in mock_logger.error.call_args[0][0]
