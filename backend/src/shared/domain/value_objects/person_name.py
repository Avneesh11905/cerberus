from dataclasses import dataclass
from typing import Any


"""
Module: Value Objects
Contains pure domain value objects encapsulating core validation logic and business rules.
"""


@dataclass(frozen=True)
class PersonName:
    """Value object representing a person's name with length and whitespace rules."""

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            object.__setattr__(self, "value", str(self.value))
        val = self.value.strip()
        if len(val) > 100:
            raise ValueError("Name too long")
        object.__setattr__(self, "value", val)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, PersonName):
            return self.value == other.value
        return False
