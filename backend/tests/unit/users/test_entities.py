from uuid import uuid4

import pytest

from src.modules.users.domain.entities import UserProfile
from src.shared.domain.value_objects import EmailAddress, HttpsUrl, PersonName


def test_user_profile_invariants():
    profile = UserProfile(
        id=uuid4(), email=EmailAddress("test@example.com"), receive_updates=True
    )

    # Valid updates
    profile.update_info(
        name=PersonName("John Doe"),
        picture=HttpsUrl("https://example.com/pic.jpg"),
        receive_updates=False,
    )
    assert profile.name == "John Doe"
    assert profile.picture == "https://example.com/pic.jpg"
    assert profile.receive_updates is False

    # Name too long
    with pytest.raises(ValueError):
        profile.update_info(name=PersonName("A" * 101))

    # (Picture URL length constraint is handled internally by Pydantic's AnyHttpUrl)


def test_user_profile_initial_validation():
    # Model validator catches non-https on creation (Now Handled by HttpsUrl if we added custom validator, but AnyHttpUrl catches invalid URLs)
    with pytest.raises(ValueError):
        UserProfile(
            id=uuid4(),
            email=EmailAddress("test@example.com"),
            receive_updates=True,
            picture=HttpsUrl("invalid-url"),
        )
