import dataclasses
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.modules.users.application.commands.user_commands import (
    DeleteAccountCommand,
    UpdateProfileCommand,
)
from src.modules.users.application.use_cases.delete_account import DeleteAccountUseCase
from src.modules.users.application.use_cases.update_profile import UpdateProfileUseCase
from src.modules.users.domain.entities import UserProfile
from src.modules.users.domain.exceptions import UserNotFoundException
from src.shared.domain.value_objects import EmailAddress


@pytest.fixture
def mock_uow(mock_profile_repo):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.profile_repo = mock_profile_repo
    uow.user_command_repo = mock_profile_repo  # just use the same mock for both
    return uow


@pytest.fixture
def mock_profile_repo():
    repo = MagicMock()
    repo.save_profile = AsyncMock()
    repo.get_profile = AsyncMock()
    repo.delete_user = AsyncMock()
    return repo


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.get_dict = AsyncMock()
    cache.delete_key = AsyncMock()
    cache.set_string = AsyncMock()
    return cache


@pytest.fixture
def dummy_profile():
    return UserProfile(
        id=uuid4(),
        email=EmailAddress("test@example.com"),
        receive_updates=True,
    )


@pytest.mark.asyncio
async def test_update_profile_cache_hit(
    mock_profile_repo, mock_cache, dummy_profile, mock_uow
):
    mock_cache.get_dict.return_value = json.loads(
        json.dumps(dataclasses.asdict(dummy_profile), default=str)
    )

    async def return_profile(profile):
        return profile

    mock_profile_repo.save_profile.side_effect = return_profile

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(
        uow=mock_uow, cache=mock_cache
    )
    command = UpdateProfileCommand(
        user_id=dummy_profile.id,
        name="New Name",
        picture="https://example.com/pic.jpg",
    )
    result = await use_case.execute(command=command)

    assert result.name == "New Name"
    assert result.picture == "https://example.com/pic.jpg"
    mock_profile_repo.get_profile.assert_not_called()
    mock_profile_repo.save_profile.assert_called_once()
    mock_cache.delete_key.assert_called_once_with(f"user_profile:{dummy_profile.id}")


@pytest.mark.asyncio
async def test_update_profile_db_fallback(
    mock_profile_repo, mock_cache, dummy_profile, mock_uow
):
    mock_cache.get_dict.return_value = None
    mock_profile_repo.get_profile.return_value = dummy_profile
    mock_profile_repo.save_profile.return_value = dummy_profile

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(
        uow=mock_uow, cache=mock_cache
    )
    command = UpdateProfileCommand(
        user_id=dummy_profile.id,
        receive_updates=False,
    )
    result = await use_case.execute(command=command)

    assert result.receive_updates is False
    mock_profile_repo.get_profile.assert_called_once_with(dummy_profile.id)


@pytest.mark.asyncio
async def test_update_profile_not_found(mock_profile_repo, mock_cache, mock_uow):
    mock_cache.get_dict.return_value = None
    mock_profile_repo.get_profile.return_value = None

    use_case: UpdateProfileUseCase = UpdateProfileUseCase(
        uow=mock_uow, cache=mock_cache
    )
    with pytest.raises(UserNotFoundException):
        command = UpdateProfileCommand(user_id=uuid4())
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_account_success(mock_profile_repo, mock_cache, mock_uow):
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(
        uow=mock_uow, cache=mock_cache
    )
    user_id = uuid4()

    command = DeleteAccountCommand(user_id=user_id, jwt_jti=None, jwt_exp=None)
    await use_case.execute(command=command)

    mock_profile_repo.delete_user.assert_called_once_with(user_id)
    mock_cache.delete_key.assert_called_once_with(f"user_profile:{user_id}")
    mock_cache.set_string.assert_not_called()


@pytest.mark.asyncio
async def test_delete_account_blacklist_jwt(
    mocker, mock_profile_repo, mock_cache, mock_uow
):
    from src.core.config import get_settings

    mocker.patch.object(get_settings().token, "ACCESS_TOKEN_LIFETIME_MINUTES", 15)
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(
        uow=mock_uow, cache=mock_cache
    )
    user_id = uuid4()

    # Simulate a token expiring in 10 minutes
    now = int(datetime.now(timezone.utc).timestamp())
    exp = now + 600

    command = DeleteAccountCommand(user_id=user_id, jwt_jti="dummy-jti", jwt_exp=exp)
    await use_case.execute(command=command)

    mock_profile_repo.delete_user.assert_called_once_with(user_id)
    # The TTL should be approximately 600 seconds
    call_args = mock_cache.set_string.call_args[0]
    assert call_args[0] == "blacklist:dummy-jti"
    assert call_args[1] == "1"
    assert 590 <= call_args[2] <= 600


@pytest.mark.asyncio
async def test_delete_account_expired_jwt(mock_profile_repo, mock_cache, mock_uow):
    use_case: DeleteAccountUseCase = DeleteAccountUseCase(
        uow=mock_uow, cache=mock_cache
    )
    user_id = uuid4()

    # Simulate a token that already expired
    now = int(datetime.now(timezone.utc).timestamp())
    exp = now - 600

    command = DeleteAccountCommand(user_id=user_id, jwt_jti="dummy-jti", jwt_exp=exp)
    await use_case.execute(command=command)

    # Because ttl <= 0, we shouldn't blacklist it
    mock_cache.set_string.assert_not_called()
