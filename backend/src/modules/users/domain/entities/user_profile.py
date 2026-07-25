from dataclasses import dataclass, field
from uuid import UUID

from src.modules.authorization.domain.enums import GlobalRole
from src.shared.domain.value_objects import EmailAddress, HttpsUrl, PersonName


"""
Defines the pure domain entity for a User Profile.
This Pydantic model contains no infrastructure dependencies (like SQLAlchemy),
ensuring the core business logic remains framework-agnostic.
"""


@dataclass(kw_only=True)
class UserProfile:
    id: UUID
    email: EmailAddress
    role: GlobalRole | str | None = None
    name: PersonName | None = None
    picture: HttpsUrl | None = None
    receive_updates: bool
    is_active: bool = True
    login_methods: list[str] = field(default_factory=list)
    custom_claims: dict = field(default_factory=dict)

    def update_info(
        self,
        name: PersonName | None = None,
        picture: HttpsUrl | None = None,
        receive_updates: bool | None = None,
    ) -> None:
        """Update profile information, enforcing invariants."""
        if name is not None:
            self.name = name
        if picture is not None:
            self.picture = picture
        if receive_updates is not None:
            self.receive_updates = receive_updates
