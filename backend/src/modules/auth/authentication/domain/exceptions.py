"""
Module: Exceptions
"""


class AuthBaseException(Exception):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(detail)


class EmailAlreadyRegisteredException(AuthBaseException):
    def __init__(self, detail: str = "Registration failed"):
        super().__init__(detail)


class InvalidCredentialsException(AuthBaseException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail)


class UnverifiedEmailException(AuthBaseException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail)


class InvalidTokenException(AuthBaseException):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail)


class NotAuthenticatedException(AuthBaseException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail)


class CSRFValidationException(AuthBaseException):
    def __init__(self, detail: str = "CSRF validation failed"):
        super().__init__(detail)


class InvalidProviderException(AuthBaseException):
    def __init__(self, detail: str = "Invalid authentication provider"):
        super().__init__(detail)


class OAuthFailedException(AuthBaseException):
    def __init__(self, detail: str = "OAuth authentication failed"):
        super().__init__(detail)


class SessionNotFoundException(AuthBaseException):
    def __init__(self, detail: str = "Session not found or does not belong to user"):
        super().__init__(detail)


class SamePasswordException(AuthBaseException):
    def __init__(
        self, detail: str = "New password must be different from the current password"
    ):
        super().__init__(detail)
