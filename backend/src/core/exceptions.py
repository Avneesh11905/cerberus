"""
Defines a global hierarchy for Domain Exceptions.
These custom exceptions abstract away HTTP status codes and presentation logic from the core business logic.
The API layer catches them and translates them into appropriate HTTP responses based on the environment.
"""

# Auth
from src.modules.authentication.domain.exceptions import (
    AuthBaseException,
)

# Projects

# Superadmin

# Users


class RateLimitExceededException(Exception):
    def __init__(self, detail: str, retry_after: int | None = None):
        self.detail = detail
        self.retry_after = retry_after


class TurnstileVerificationFailed(AuthBaseException):
    pass


class DomainException(Exception):
    pass
