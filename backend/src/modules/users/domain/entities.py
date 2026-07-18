"""
Defines the pure domain entity for a User Profile.
This Pydantic model contains no infrastructure dependencies (like SQLAlchemy),
ensuring the core business logic remains framework-agnostic.
"""

from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.modules.auth.authorization.domain.enums import ProjectRole, GlobalRole


class UserProfile(BaseModel):
    id: UUID
    email: str
    role: GlobalRole | ProjectRole
    project_id: UUID | None = None
    name: str | None = None
    picture: str | None = None
    receive_updates: bool
    is_active: bool = True
    login_methods: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_picture(self) -> "UserProfile":
        if self.picture is not None and not self.picture.startswith("https://"):
            raise ValueError("Profile picture must be an HTTPS URL")
        return self

    def update_info(
        self,
        name: str | None = None,
        picture: str | None = None,
        receive_updates: bool | None = None,
    ) -> None:
        """Update profile information, enforcing invariants."""
        if name is not None:
            if len(name) > 100:
                raise ValueError("Name is too long")
            self.name = name
        if picture is not None:
            if len(picture) > 2048:
                raise ValueError("Picture URL is too long")
            if not picture.startswith("https://"):
                raise ValueError("Profile picture must be an HTTPS URL")
            self.picture = picture
        if receive_updates is not None:
            self.receive_updates = receive_updates
