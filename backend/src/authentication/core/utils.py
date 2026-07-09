import hashlib
import hmac

from src.shared.config import app_settings


def hash_otp(otp: str) -> str:
    """Hashes an OTP securely using HMAC-SHA256 with the application's session secret."""
    secret = app_settings.SESSION_SECRET.encode()
    return hmac.new(secret, otp.encode(), hashlib.sha256).hexdigest()


def verify_otp_hash(provided_otp: str, stored_hash: str) -> bool:
    """Verifies a provided OTP against the stored HMAC hash securely."""
    expected_hash = hash_otp(provided_otp)
    return hmac.compare_digest(expected_hash, stored_hash)


def anonymize_email(email: str) -> str:
    """Anonymize email address for logging to prevent PII leakage."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[:3]}***@{domain}"


def format_device_info(user_agent_str: str | None) -> str:
    """Parses a raw user agent string and returns a human-readable device/browser info."""
    if not user_agent_str:
        return "Unknown Device"
    
    try:
        from user_agents import parse  # type: ignore[import-untyped]
        ua = parse(user_agent_str)
        
        browser = ua.browser.family if ua.browser.family else "Unknown Browser"
        os_name = ua.os.family if ua.os.family else "Unknown OS"
        
        if ua.is_mobile:
            device_type = "Mobile Device"
        elif ua.is_tablet:
            device_type = "Tablet"
        elif ua.is_pc:
            device_type = "PC"
        elif ua.is_bot:
            device_type = "Bot"
        else:
            device_type = "Device"
            
        return f"{browser} on {os_name} ({device_type})"
    except Exception:
        return "Unknown Device"
