"""
Executes database queries for user profiles using SQLAlchemy.
Maps raw database rows into pure `UserProfile` domain entities to prevent ORM leakage.
"""

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.authentication.application.ports import RefreshTokenRepositoryPort
from src.modules.users.application.ports import UserProfileRepositoryPort
from src.modules.users.domain.entities import UserProfile
from src.modules.users.domain.exceptions import UserNotFoundException
from src.modules.users.infrastructure.models import User
from src.shared.domain.value_objects import EmailAddress, HttpsUrl, PersonName


class SQLUserProfileRepositoryAdapter(UserProfileRepositoryPort):
    """Implements UserProfileRepositoryPort using SQLAlchemy."""

    def __init__(self, session: AsyncSession, refresh_repo: RefreshTokenRepositoryPort):
        self._session = session
        self._refresh_repo = refresh_repo

    def _to_profile(self, user: User) -> UserProfile:
        methods = []
        if user.password:
            methods.append("local")
        for account in user.oauth_accounts:
            methods.append(account.provider)

        return UserProfile(
            id=user.id,
            email=EmailAddress(user.email),
            role=None,
            name=PersonName(user.name) if user.name else None,
            picture=HttpsUrl(user.picture) if user.picture else None,
            receive_updates=user.receive_updates,
            is_active=user.is_active,
            login_methods=methods,
            custom_claims=user.custom_claims,
        )

    async def get_profile(self, user_id: UUID) -> UserProfile | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return self._to_profile(user)

        # Fallback to Tenant
        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await self._session.execute(
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
            email=EmailAddress(tenant.email),
            role=tenant.role,
            name=PersonName(tenant.name) if tenant.name else None,
            picture=HttpsUrl(cast(str, tenant.picture)) if tenant.picture else None,
            receive_updates=tenant.receive_updates,
            is_active=tenant.is_active,
            login_methods=methods,
            custom_claims={},
        )

    async def save_profile(self, profile: UserProfile) -> UserProfile:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == profile.id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.name = profile.name.value if profile.name else None
            user.picture = profile.picture.value if profile.picture else None
            user.receive_updates = profile.receive_updates
            await self._session.flush()
            return self._to_profile(user)

        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await self._session.execute(
            select(Tenant)
            .options(selectinload(Tenant.oauth_accounts))
            .options(selectinload(Tenant.password))
            .where(Tenant.id == profile.id)
        )
        tenant = tenant_res.scalar_one_or_none()
        if not tenant:
            raise UserNotFoundException()

        tenant.name = profile.name.value if profile.name else None
        tenant.picture = profile.picture.value if profile.picture else None
        tenant.receive_updates = profile.receive_updates
        await self._session.flush()

        methods = []
        if tenant.password:
            methods.append("local")
        for account in tenant.oauth_accounts:
            methods.append(account.provider)

        return UserProfile(
            id=tenant.id,
            email=EmailAddress(tenant.email),
            role=tenant.role,
            name=PersonName(tenant.name) if tenant.name else None,
            picture=HttpsUrl(cast(str, tenant.picture)) if tenant.picture else None,
            receive_updates=tenant.receive_updates,
            is_active=tenant.is_active,
            login_methods=methods,
            custom_claims={},
        )

    async def delete_user(self, user_id: UUID) -> None:
        """Hard delete a user (cascades to projects, oauth, tokens)."""
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await self._refresh_repo.revoke_all_for_user(user_id)
            await self._session.delete(user)
            await self._session.flush()
            return

        from src.modules.superadmin.infrastructure.models import Tenant

        tenant_res = await self._session.execute(
            select(Tenant).where(Tenant.id == user_id)
        )
        tenant = tenant_res.scalar_one_or_none()
        if tenant:
            await self._refresh_repo.revoke_all_for_user(user_id)
            await self._session.delete(tenant)
            await self._session.flush()
