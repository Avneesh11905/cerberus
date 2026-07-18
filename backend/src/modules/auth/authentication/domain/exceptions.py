"""
Module: Exceptions
"""


class AuthBaseException(Exception):
    pass


class EmailAlreadyRegisteredException(AuthBaseException):
    pass


class InvalidCredentialsException(AuthBaseException):
    pass


class UnverifiedEmailException(AuthBaseException):
    pass


class InvalidTokenException(AuthBaseException):
    pass


class NotAuthenticatedException(AuthBaseException):
    pass


class CSRFValidationException(AuthBaseException):
    pass


class InvalidProviderException(AuthBaseException):
    pass


class OAuthFailedException(AuthBaseException):
    pass


class SessionNotFoundException(AuthBaseException):
    pass


class SamePasswordException(AuthBaseException):
    pass
