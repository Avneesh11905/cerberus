from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    TENANT = "TENANT"
    USER = "USER"


class EventType(str, Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    OTP_ABUSE_ATTEMPT = "OTP_ABUSE_ATTEMPT"
    REGISTRATION = "REGISTRATION"
    API_REQUEST = "API_REQUEST"
    PASSWORD_RESET = "PASSWORD_RESET"
    OTP_SENT = "OTP_SENT"


class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
