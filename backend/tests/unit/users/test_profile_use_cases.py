import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from src.modules.users.application.use_cases.update_profile import UpdateProfileUseCase
from src.modules.users.application.use_cases.delete_account import DeleteAccountUseCase
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.domain.entities import UserProfile


@pytest.fixture
def mock_profile_repo():
    return AsyncMock()


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def dummy_profile():
    return UserProfile(
        id=uuid4(),
        email="test@example.com",
        receive_updates=True,
    )


@pytest.mark.asyncio
async def test_update_profile_cache_hit(mock_profile_repo, mock_cache, dummy_profile):
    mock_cache.get_dict.return_value = dummy_profile.model_dump(mode="json")

    async def return_profile(session, profile):
        return profile

    mock_profile_repo.save_profile.side_effect = return_profile

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(mock_profile_repo, mock_cache)
    result = await use_case.execute(
        session=None,
        user_id=dummy_profile.id,
        name="New Name",
        picture="https://example.com/pic.jpg",
    )

    assert result.name == "New Name"
    assert result.picture == "https://example.com/pic.jpg"
    mock_profile_repo.get_profile.assert_not_called()
    mock_profile_repo.save_profile.assert_called_once()
    mock_cache.delete_key.assert_called_once_with(f"user_profile:{dummy_profile.id}")


@pytest.mark.asyncio
async def test_update_profile_db_fallback(mock_profile_repo, mock_cache, dummy_profile):
    mock_cache.get_dict.return_value = None
    mock_profile_repo.get_profile.return_value = dummy_profile
    mock_profile_repo.save_profile.return_value = dummy_profile

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(mock_profile_repo, mock_cache)
    result = await use_case.execute(
        session=None,
        user_id=dummy_profile.id,
        receive_updates=False,
    )

    assert result.receive_updates is False
    mock_profile_repo.get_profile.assert_called_once_with(None, dummy_profile.id)


@pytest.mark.asyncio
async def test_update_profile_not_found(mock_profile_repo, mock_cache):
    mock_cache.get_dict.return_value = None
    mock_profile_repo.get_profile.return_value = None

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(mock_profile_repo, mock_cache)
    with pytest.raises(UserNotFoundException):
        await use_case.execute(session=None, user_id=uuid4())


@pytest.mark.asyncio
async def test_delete_account_success(mock_profile_repo, mock_cache):
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(mock_profile_repo, mock_cache)
    user_id = uuid4()

    await use_case.execute(session=None, user_id=user_id, jwt_jti=None, jwt_exp=None)

    mock_profile_repo.delete_user.assert_called_once_with(None, user_id)
    mock_cache.delete_key.assert_called_once_with(f"user_profile:{user_id}")
    mock_cache.set_string.assert_not_called()


@pytest.mark.asyncio
@patch("src.modules.users.application.use_cases.delete_account.token_settings")
async def test_delete_account_blacklist_jwt(
    mock_token_settings, mock_profile_repo, mock_cache
):
    mock_token_settings.ACCESS_TOKEN_LIFETIME_MINUTES = 15
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(mock_profile_repo, mock_cache)
    user_id = uuid4()

    # Simulate a token expiring in 10 minutes
    now = int(datetime.now(timezone.utc).timestamp())
    exp = now + 600

    await use_case.execute(
        session=None, user_id=user_id, jwt_jti="dummy-jti", jwt_exp=exp
    )

    mock_profile_repo.delete_user.assert_called_once_with(None, user_id)
    # The TTL should be approximately 600 seconds
    call_args = mock_cache.set_string.call_args[0]
    assert call_args[0] == "blacklist:dummy-jti"
    assert call_args[1] == "1"
    assert 590 <= call_args[2] <= 600


@pytest.mark.asyncio
async def test_delete_account_expired_jwt(mock_profile_repo, mock_cache):
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(mock_profile_repo, mock_cache)
    user_id = uuid4()

    # Simulate a token that already expired
    now = int(datetime.now(timezone.utc).timestamp())
    exp = now - 600

    await use_case.execute(
        session=None, user_id=user_id, jwt_jti="dummy-jti", jwt_exp=exp
    )

    # Because ttl <= 0, we shouldn't blacklist it
    mock_cache.set_string.assert_not_called()
