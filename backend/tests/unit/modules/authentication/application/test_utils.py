from src.modules.authentication.application.utils import (
    anonymize_email,
    format_device_info,
    hash_otp,
    verify_otp_hash,
)


def test_hash_otp_determinism():
    otp = "123456"
    assert hash_otp(otp) == hash_otp(otp)


def test_verify_otp_hash():
    otp = "123456"
    h = hash_otp(otp)
    assert verify_otp_hash(otp, h) is True
    assert verify_otp_hash("wrong", h) is False


def test_anonymize_email():
    assert anonymize_email("admin@example.com") == "adm***@example.com"
    assert anonymize_email("a@b.com") == "a***@b.com"
    assert anonymize_email("invalid") == "***"


def test_format_device_info():
    assert "Unknown Device" in format_device_info(None)
    assert "Unknown Device" in format_device_info("")

    mobile = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    assert "Mobile Device" in format_device_info(mobile)

    pc = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    assert "PC" in format_device_info(pc)

    tablet = "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    assert "Tablet" in format_device_info(tablet)

    bot = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    assert "Bot" in format_device_info(bot)

    generic = "python-requests/2.25.1"
    assert "Device" in format_device_info(generic)


def test_format_device_info_exception(mocker):
    mocker.patch("user_agents.parse", side_effect=Exception("Parsing error"))
    assert format_device_info("some-agent") == "Unknown Device"
