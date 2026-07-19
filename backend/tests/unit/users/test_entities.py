import pytest
from uuid import uuid4

from src.modules.users.domain.entities import UserProfile


def test_user_profile_invariants():
    profile = UserProfile(id=uuid4(), email="test@example.com", receive_updates=True)

    # Valid updates
    profile.update_info(
        name="John Doe", picture="https://example.com/pic.jpg", receive_updates=False
    )
    assert profile.name == "John Doe"
    assert profile.picture == "https://example.com/pic.jpg"
    assert profile.receive_updates is False

    # Name too long
    with pytest.raises(ValueError, match="Name is too long"):
        profile.update_info(name="A" * 101)

    # Picture URL too long
    with pytest.raises(ValueError, match="Picture URL is too long"):
        profile.update_info(picture="https://" + "A" * 2041)

    # Picture must be https
    with pytest.raises(ValueError, match="Profile picture must be an HTTPS URL"):
        profile.update_info(picture="http://example.com/pic.jpg")


def test_user_profile_initial_validation():
    # Model validator catches non-https on creation
    with pytest.raises(ValueError, match="Profile picture must be an HTTPS URL"):
        UserProfile(
            id=uuid4(),
            email="test@example.com",
            receive_updates=True,
            picture="http://example.com",
        )
