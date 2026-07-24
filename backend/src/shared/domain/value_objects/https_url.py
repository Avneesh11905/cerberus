from dataclasses import dataclass
from typing import Any


"""
Module: Value Objects
Contains pure domain value objects encapsulating core validation logic and business rules.
"""


@dataclass(frozen=True)
class HttpsUrl:
    """Value object representing an HTTPS URL with a maximum length limit."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            object.__setattr__(self, "value", str(self.value))
        if not self.value.startswith("https://") and not self.value.startswith(
            "http://localhost"
        ):
            raise ValueError("Must be an HTTPS URL or http://localhost")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, HttpsUrl):
            return self.value == other.value
        return False
