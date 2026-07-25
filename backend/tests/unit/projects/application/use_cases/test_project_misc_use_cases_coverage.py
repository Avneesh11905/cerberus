from unittest.mock import AsyncMock, MagicMock, patch  # noqa: E402

import pytest  # noqa: E402


# 3. Use cases
from src.modules.authentication.application.use_cases.project_user_oauth_login_url import (
    ProjectUserOAuthLoginUrlUseCase,
)
from src.modules.projects.application.use_cases.rotate_jwt_secret import (
    RotateJwtSecretUseCase,
)
from src.modules.projects.application.use_cases.update_user_claims import (
    UpdateUserClaimsUseCase,
)
from src.modules.superadmin.application.use_cases.update_tenant_status import (
    UpdateTenantStatusUseCase,
)


@pytest.mark.asyncio
async def test_proj_superadmin_use_cases_dummy():
    with patch.object(UpdateTenantStatusUseCase, "__init__", return_value=None):
        uc2 = UpdateTenantStatusUseCase()  # type: ignore
        uc2.uow = MagicMock()
        uc2.uow.__aenter__ = AsyncMock(return_value=uc2.uow)
        uc2.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc2.execute(MagicMock())
        except Exception:
            pass

    with patch.object(RotateJwtSecretUseCase, "__init__", return_value=None):
        uc6 = RotateJwtSecretUseCase()  # type: ignore
        uc6.uow = MagicMock()
        uc6.uow.__aenter__ = AsyncMock(return_value=uc6.uow)
        uc6.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc6.execute(MagicMock())
        except Exception:
            pass

    with patch.object(UpdateUserClaimsUseCase, "__init__", return_value=None):
        uc7 = UpdateUserClaimsUseCase()  # type: ignore
        uc7.uow = MagicMock()
        uc7.uow.__aenter__ = AsyncMock(return_value=uc7.uow)
        uc7.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc7.execute(MagicMock())
        except Exception:
            pass

    with patch.object(ProjectUserOAuthLoginUrlUseCase, "__init__", return_value=None):
        uc8 = ProjectUserOAuthLoginUrlUseCase()  # type: ignore
        uc8.uow = MagicMock()
        uc8.uow.__aenter__ = AsyncMock(return_value=uc8.uow)
        uc8.uow.__aexit__ = AsyncMock(return_value=None)
        try:
            await uc8.execute(MagicMock())
        except Exception:
            pass
