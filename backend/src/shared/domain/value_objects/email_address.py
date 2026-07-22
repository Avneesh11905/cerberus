from dataclasses import dataclass
from typing import Any


"""
Module: Value Objects
Contains pure domain value objects encapsulating core validation logic and business rules.
"""


@dataclass(frozen=True)
class EmailAddress:
    """Value object representing a valid email address, always normalized to lowercase."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            object.__setattr__(self, "value", str(self.value))
        val = self.value.lower().strip()
        if "@" not in val:
            raise ValueError("Invalid email format")
        object.__setattr__(self, "value", val)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, EmailAddress):
            return self.value == other.value
        return False
