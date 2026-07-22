"""
Adapter: SQL User Command Repository
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.authentication.application.ports import UserCommandRepositoryPort
from src.modules.authentication.domain.entities import UserIdentity
from src.modules.authentication.infrastructure.models import OAuthAccount, Password
from src.modules.authorization.domain.enums import GlobalRole
from src.modules.superadmin.infrastructure.models import Tenant
from src.modules.users.infrastructure.models import User

from .user_utils import to_identity


class SQLUserCommandRepositoryAdapter(UserCommandRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    """Implements user command repository ports using SQLAlchemy."""

    async def create_user_with_oauth(
        self,
        email: str,
        name: str | None,
        picture: str | None,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
        role: GlobalRole | str | None = None,
    ) -> UserIdentity:
        """Create a new user and link an OAuth account."""
        if project_id:
            user = User(
                email=email,
                name=name,
                picture=picture,
                is_verified=True,
                project_id=project_id,
                role=None,  # DB still has column, it defaults safely or stores null
            )
            self._session.add(user)
            await self._session.flush()
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                oauth_sub=oauth_sub,
            )
        else:
            tenant = Tenant(
                email=email,
                name=name,
                picture=picture,
                is_verified=True,
                role=role,
            )
            self._session.add(tenant)
            await self._session.flush()
            oauth_account = OAuthAccount(
                tenant_id=tenant.id,
                provider=provider,
                oauth_sub=oauth_sub,
            )

        self._session.add(oauth_account)
        await self._session.flush()
        if project_id:
            await self._session.refresh(user)
            return to_identity(user)
        else:
            await self._session.refresh(tenant)
            return to_identity(tenant)

    async def link_oauth_account(
        self,
        user_id: UUID,
        provider: str,
        oauth_sub: str,
        project_id: UUID | None = None,
    ) -> None:
        """Link a new OAuth provider to an existing user."""
        if project_id:
            account = OAuthAccount(
                user_id=user_id,
                provider=provider,
                oauth_sub=oauth_sub,
            )
        else:
            account = OAuthAccount(
                tenant_id=user_id,
                provider=provider,
                oauth_sub=oauth_sub,
            )
        self._session.add(account)

    async def create_user_with_password(
        self,
        email: str,
        name: str | None,
        password_hash: str | None,
        is_verified: bool = False,
        project_id: UUID | None = None,
        role: GlobalRole | str | None = None,
    ) -> UserIdentity:
        """Create a new user and store their local password."""
        if project_id:
            user = User(
                email=email,
                name=name,
                is_verified=is_verified,
                project_id=project_id,
                role=None,
            )
            self._session.add(user)
            await self._session.flush()
            if password_hash is not None:
                user_password = Password(user_id=user.id, password_hash=password_hash)
                self._session.add(user_password)
        else:
            tenant = Tenant(
                email=email,
                name=name,
                is_verified=is_verified,
                role=role,
            )
            self._session.add(tenant)
            await self._session.flush()
            if password_hash is not None:
                user_password = Password(
                    tenant_id=tenant.id, password_hash=password_hash
                )
                self._session.add(user_password)

        await self._session.flush()
        if project_id:
            await self._session.refresh(user)
            return to_identity(user)
        else:
            await self._session.refresh(tenant)
            return to_identity(tenant)

    async def update_password(
        self,
        user_id: UUID,
        password_hash: str,
        is_tenant: bool = False,
    ) -> None:
        """Update or insert a password for a user."""
        result = await self._session.execute(
            select(Password).where(
                (Password.user_id == user_id) | (Password.tenant_id == user_id)
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.password_hash = password_hash
        else:
            # We must know if it's a tenant or user for insert
            user = await self._session.execute(select(User).where(User.id == user_id))
            if user.scalar_one_or_none():
                record = Password(user_id=user_id, password_hash=password_hash)
            else:
                record = Password(tenant_id=user_id, password_hash=password_hash)
            self._session.add(record)

    async def disable_local_login(self, user_id: UUID) -> None:
        """Disable local password login by deleting the user password."""
        result = await self._session.execute(
            select(Password).where(
                (Password.user_id == user_id) | (Password.tenant_id == user_id)
            )
        )
        record = result.scalar_one_or_none()
        if record:
            await self._session.delete(record)

    async def verify_user_email(self, user_id: UUID, name: str | None = None) -> None:
        """Mark a user as verified."""
        user = await self._session.execute(select(User).where(User.id == user_id))
        user_obj = user.scalar_one_or_none()
        if user_obj:
            user_obj.is_verified = True
            if name:
                user_obj.name = name
        else:
            tenant = await self._session.execute(
                select(Tenant).where(Tenant.id == user_id)
            )
            tenant_obj = tenant.scalar_one_or_none()
            if tenant_obj:
                tenant_obj.is_verified = True
                if name:
                    tenant_obj.name = name

    async def delete_user(self, user_id: UUID) -> None:
        """Soft delete a user."""
        user = await self._session.execute(select(User).where(User.id == user_id))
        user_obj = user.scalar_one_or_none()
        if user_obj:
            user_obj.is_active = False
            user_obj.deleted_at = datetime.now(timezone.utc)
        else:
            tenant = await self._session.execute(
                select(Tenant).where(Tenant.id == user_id)
            )
            tenant_obj = tenant.scalar_one_or_none()
            if tenant_obj:
                tenant_obj.is_active = False
                tenant_obj.deleted_at = datetime.now(timezone.utc)

    async def undelete_user(self, user_id: UUID) -> None:
        """Clear the deleted_at flag to restore a soft-deleted user."""
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.deleted_at = None
        else:
            tenant = await self._session.execute(
                select(Tenant).where(Tenant.id == user_id)
            )
            tenant_obj = tenant.scalar_one_or_none()
            if tenant_obj:
                tenant_obj.deleted_at = None

    async def update_role(self, user_id: UUID, role: GlobalRole) -> None:
        """Persist a role change for a tenant. Used for admin self-heal recovery."""
        tenant_res = await self._session.execute(
            select(Tenant).where(Tenant.id == user_id)
        )
        tenant = tenant_res.scalar_one_or_none()
        if tenant:
            tenant.role = role
