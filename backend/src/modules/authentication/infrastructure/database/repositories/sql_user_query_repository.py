"""
Adapter: SQL User Query Repository
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.authentication.application.ports import UserQueryRepositoryPort
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.infrastructure.models import OAuthAccount, Password
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User

from .user_utils import to_identity


class SQLUserQueryRepositoryAdapter(UserQueryRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    """Implements user query repository ports using SQLAlchemy."""

    async def find_by_id(self, user_id: UUID) -> UserIdentity | None:
        """Look up a user by their ID."""
        user_stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(user_stmt)
        user = result.scalar_one_or_none()
        if user:
            return to_identity(user)

        tenant_stmt = select(Tenant).where(Tenant.id == user_id)
        tenant_result = await self._session.execute(tenant_stmt)
        tenant = tenant_result.scalar_one_or_none()
        if tenant:
            return to_identity(tenant)

        return None

    async def find_by_oauth(
        self,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> UserIdentity | None:
        """Look up a user by their OAuth provider + subject ID within a project."""

        if project_id:
            user_stmt = (
                select(User)
                .join(OAuthAccount, OAuthAccount.user_id == User.id)
                .where(
                    OAuthAccount.provider == provider,
                    OAuthAccount.oauth_sub == oauth_sub,
                    User.project_id == project_id,
                )
            )
            result = await self._session.execute(user_stmt)
            user = result.scalar_one_or_none()
            return to_identity(user) if user else None
        else:
            tenant_stmt = (
                select(Tenant)
                .join(OAuthAccount, OAuthAccount.tenant_id == Tenant.id)
                .where(
                    OAuthAccount.provider == provider,
                    OAuthAccount.oauth_sub == oauth_sub,
                )
            )
            tenant_result = await self._session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one_or_none()
            return to_identity(tenant) if tenant else None

    async def find_by_email(
        self, email: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        """Look up a user by email within a project."""
        if project_id:
            user_stmt = select(User).where(
                User.email == email, User.project_id == project_id
            )
            result = await self._session.execute(user_stmt)
            user = result.scalar_one_or_none()
            return to_identity(user) if user else None
        else:
            tenant_stmt = select(Tenant).where(Tenant.email == email)
            tenant_result = await self._session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one_or_none()
            return to_identity(tenant) if tenant else None

    async def find_password_hash(
        self, user_id: UUID, is_tenant: bool = False
    ) -> str | None:
        """Look up the password hash for a given user ID."""
        stmt = select(Password).where(
            (Password.user_id == user_id) | (Password.tenant_id == user_id)
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()
        return record.password_hash if record else None
