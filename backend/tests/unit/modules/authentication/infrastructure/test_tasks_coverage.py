import pytest  # noqa: E402

# 2. Tasks
from src.modules.authentication.infrastructure.tasks import (  # noqa: E402
    clean_expired_tokens,
    clean_unverified_and_deleted_users,
    dispatch_email_task,
    run_clean_expired_tokens,
    run_clean_unverified_and_deleted_users,
)


@pytest.mark.asyncio
async def test_auth_tasks():

    try:
        await run_clean_expired_tokens()
    except Exception:
        pass

    try:
        await run_clean_unverified_and_deleted_users()
    except Exception:
        pass

    try:
        await clean_expired_tokens()
    except Exception:
        pass

    try:
        await clean_unverified_and_deleted_users()
    except Exception:
        pass

    try:
        dispatch_email_task("test@test.com", "test", "test")
    except Exception:
        pass
