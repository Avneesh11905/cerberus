"""
Adapter: SQL User Query Repository
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.ports import UserQueryRepositoryPort
from src.modules.auth.domain.entities import UserIdentity
from src.modules.auth.infrastructure.models import OAuthAccount, Password
from src.modules.projects.infrastructure.models import Project
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User

from .user_utils import to_identity


class SQLUserQueryRepositoryAdapter(UserQueryRepositoryPort[AsyncSession]):
    """Implements user query repository ports using SQLAlchemy."""

    async def find_by_id(
        self, session: AsyncSession, user_id: UUID
    ) -> UserIdentity | None:
        """Look up a user by their ID."""
        user_stmt = select(User).where(User.id == user_id)
        result = await session.execute(user_stmt)
        user = result.scalar_one_or_none()
        if user:
            return to_identity(user)

        tenant_stmt = select(Tenant).where(Tenant.id == user_id)
        tenant_result = await session.execute(tenant_stmt)
        tenant = tenant_result.scalar_one_or_none()
        if tenant:
            return to_identity(tenant)

        return None

    async def find_by_oauth(
        self,
        session: AsyncSession,
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
            result = await session.execute(user_stmt)
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
            tenant_result = await session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one_or_none()
            return to_identity(tenant) if tenant else None

    async def find_by_email(
        self, session: AsyncSession, email: str, project_id: UUID | None = None
    ) -> UserIdentity | None:
        """Look up a user by email within a project."""
        if project_id:
            user_stmt = select(User).where(
                User.email == email, User.project_id == project_id
            )
            result = await session.execute(user_stmt)
            user = result.scalar_one_or_none()
            return to_identity(user) if user else None
        else:
            tenant_stmt = select(Tenant).where(Tenant.email == email)
            tenant_result = await session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one_or_none()
            return to_identity(tenant) if tenant else None

    async def find_password_hash(
        self, session: AsyncSession, user_id: UUID, is_tenant: bool = False
    ) -> str | None:
        """Look up the password hash for a given user ID."""
        stmt = select(Password).where(
            (Password.user_id == user_id) | (Password.tenant_id == user_id)
        )
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()
        return record.password_hash if record else None

    async def is_project_admin(
        self, session: AsyncSession, project_id: UUID, email: str
    ) -> bool:
        """Check if an email is an admin/owner for the project."""
        stmt = select(User).where(User.project_id == project_id, User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user and user.role == "admin":
            return True

        # Also check if it's the tenant owner
        stmt_tenant = (
            select(Tenant)
            .join(Project, Project.tenant_id == Tenant.id)
            .where(Project.id == project_id, Tenant.email == email)
        )
        result_tenant = await session.execute(stmt_tenant)
        return result_tenant.scalar_one_or_none() is not None
