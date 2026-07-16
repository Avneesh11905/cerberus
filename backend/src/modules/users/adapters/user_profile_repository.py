"""
Executes database queries for user profiles using SQLAlchemy.
Maps raw database rows into pure `UserProfile` domain entities to prevent ORM leakage.
"""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.auth.application.ports.repository.refresh_token import (
    RefreshTokenRepositoryPort,
)
from src.modules.users.domain import UserProfile
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.infrastructure.models import User


class SQLUserProfileRepository:
    """Implements UserProfileRepositoryPort using SQLAlchemy."""

    def __init__(self, refresh_repo: RefreshTokenRepositoryPort):
        self._refresh_repo = refresh_repo

    def _to_profile(self, user: User) -> UserProfile:
        methods = []
        if user.password:
            methods.append("local")
        for account in user.oauth_accounts:
            methods.append(account.provider)

        return UserProfile(
            id=user.id,
            email=user.email,
            role=user.role,
            project_id=user.project_id if user.project_id else None,
            name=user.name,
            picture=user.picture,
            receive_updates=user.receive_updates,
            is_active=user.is_active,
            login_methods=methods,
        )

    async def get_profile(
        self, session: AsyncSession, user_id: UUID
    ) -> UserProfile | None:
        result = await session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return self._to_profile(user)

        # Fallback to Tenant
        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await session.execute(
            select(Tenant)
            .options(selectinload(Tenant.oauth_accounts))
            .options(selectinload(Tenant.password))
            .where(Tenant.id == user_id)
        )
        tenant = tenant_res.scalar_one_or_none()
        if not tenant:
            return None

        methods = []
        if tenant.password:
            methods.append("local")
        for account in tenant.oauth_accounts:
            methods.append(account.provider)

        return UserProfile(
            id=tenant.id,
            email=tenant.email,
            role=tenant.role,
            project_id=None,
            name=tenant.name,
            picture=cast(str, tenant.picture) if tenant.picture else None,
            receive_updates=tenant.receive_updates,
            is_active=tenant.is_active,
            login_methods=methods,
        )

    async def save_profile(
        self, session: AsyncSession, profile: UserProfile
    ) -> UserProfile:
        result = await session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == profile.id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.name = profile.name
            user.picture = profile.picture
            user.receive_updates = profile.receive_updates
            await session.flush()
            return self._to_profile(user)

        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await session.execute(
            select(Tenant)
            .options(selectinload(Tenant.oauth_accounts))
            .options(selectinload(Tenant.password))
            .where(Tenant.id == profile.id)
        )
        tenant = tenant_res.scalar_one_or_none()
        if not tenant:
            raise UserNotFoundException()

        tenant.name = profile.name
        tenant.picture = profile.picture
        tenant.receive_updates = profile.receive_updates
        await session.flush()

        methods = []
        if tenant.password:
            methods.append("local")
        for account in tenant.oauth_accounts:
            methods.append(account.provider)

        return UserProfile(
            id=tenant.id,
            email=tenant.email,
            role=tenant.role,
            project_id=None,
            name=tenant.name,
            picture=cast(str, tenant.picture) if tenant.picture else None,
            receive_updates=tenant.receive_updates,
            is_active=tenant.is_active,
            login_methods=methods,
        )

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> None:
        """Hard delete a user (cascades to projects, oauth, tokens)."""
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await self._refresh_repo.revoke_all_for_user(session, user_id)
            await session.delete(user)
            await session.flush()
            return

        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await session.execute(select(Tenant).where(Tenant.id == user_id))
        tenant = tenant_res.scalar_one_or_none()
        if tenant:
            await self._refresh_repo.revoke_all_for_user(session, user_id)
            await session.delete(tenant)
            await session.flush()
