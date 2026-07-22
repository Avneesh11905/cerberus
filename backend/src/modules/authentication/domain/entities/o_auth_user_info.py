from dataclasses import dataclass

from src.shared.domain.value_objects import EmailAddress, HttpsUrl


"""
Module: Session
Contains pure domain entities related to tracking user sessions and devices.
"""


@dataclass(kw_only=True)
class OAuthUserInfo:
    """Structured data returned by OAuth providers."""

    provider: str
    sub: str
    email: EmailAddress
    name: str | None = None
    picture: HttpsUrl | None = None
