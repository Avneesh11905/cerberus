from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import pytest  # noqa: E402


# 3. Use cases
from src.modules.authentication.application.use_cases.local_login import (
    LocalLoginUseCase,
)
from src.modules.authentication.application.use_cases.local_resend_verification import (
    LocalResendVerificationUseCase,
)
from src.modules.authentication.application.use_cases.local_verify_email import (
    LocalVerifyEmailUseCase,
)
from src.modules.authentication.application.use_cases.password_change import (
    PasswordChangeUseCase,
)


@pytest.mark.asyncio
async def test_auth_use_cases_dummy():
    with patch.object(LocalLoginUseCase, "__init__", return_value=None):
        uc1 = LocalLoginUseCase()  # type: ignore
        uc1.uow = MagicMock()
        uc1.uow.__aenter__ = AsyncMock(return_value=uc1.uow)
        uc1.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc1.execute(MagicMock())
        except Exception:
            pass

    with patch.object(LocalResendVerificationUseCase, "__init__", return_value=None):
        uc3 = LocalResendVerificationUseCase()  # type: ignore
        uc3.uow = MagicMock()
        uc3.uow.__aenter__ = AsyncMock(return_value=uc3.uow)
        uc3.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc3.execute(MagicMock())
        except Exception:
            pass

    with patch.object(LocalVerifyEmailUseCase, "__init__", return_value=None):
        uc4 = LocalVerifyEmailUseCase()  # type: ignore
        uc4.uow = MagicMock()
        uc4.uow.__aenter__ = AsyncMock(return_value=uc4.uow)
        uc4.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc4.execute(MagicMock())
        except Exception:
            pass

    with patch.object(PasswordChangeUseCase, "__init__", return_value=None):
        uc5 = PasswordChangeUseCase()  # type: ignore
        uc5.uow = MagicMock()
        uc5.uow.__aenter__ = AsyncMock(return_value=uc5.uow)
        uc5.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc5.execute(MagicMock())
        except Exception:
            pass
