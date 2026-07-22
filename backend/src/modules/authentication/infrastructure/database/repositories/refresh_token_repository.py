"""
Handles reading and writing Refresh Tokens.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid6 import uuid7

from src.modules.authentication.application.ports import RefreshTokenRepositoryPort
from src.modules.authentication.domain.entities import ActiveSession, UserIdentity
from src.modules.authentication.infrastructure.models import RefreshToken
from src.modules.users.infrastructure.models import User
from src.shared.application.ports import CachePort
from src.shared.domain.entities import ClientMetadata
from src.shared.domain.value_objects import EmailAddress, HttpsUrl

from .refresh_token_utils import cache_key, hash_token


class DBRefreshTokenRepositoryAdapter(RefreshTokenRepositoryPort):
    """Implements RefreshTokenRepositoryPort using SQL database."""

    def __init__(
        self,
        session: AsyncSession,
        lifetime_days: int,
        cache: "CachePort | None" = None,
    ):
        self._session = session
        self._lifetime_days = lifetime_days
        self._cache = cache

    async def create(
        self,
        user_id: UUID,
        family_id: UUID | None = None,
        auth_provider: str = "local",
        client_meta: ClientMetadata | None = None,
    ) -> str:
        """Create a new refresh token. Returns the raw token."""
        raw_token = secrets.token_urlsafe(64)
        hashed = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=self._lifetime_days)

        ip_addr = client_meta.ip_address if client_meta else None
        u_agent = client_meta.user_agent if client_meta else None

        # Check if user_id belongs to a User or Tenant
        from sqlalchemy import select

        from src.modules.users.infrastructure.models import User

        user_res = await self._session.execute(select(User).where(User.id == user_id))
        if user_res.scalar_one_or_none():
            refresh = RefreshToken(
                token=hashed,
                user_id=user_id,
                family_id=family_id or uuid7(),
                expires_at=expires_at,
                auth_provider=auth_provider,
                ip_address=ip_addr,
                user_agent=u_agent,
            )
        else:
            refresh = RefreshToken(
                token=hashed,
                tenant_id=user_id,
                family_id=family_id or uuid7(),
                expires_at=expires_at,
                auth_provider=auth_provider,
                ip_address=ip_addr,
                user_agent=u_agent,
            )
        self._session.add(refresh)
        await self._session.flush()
        return raw_token

    async def _revoke_family(self, family_id: UUID) -> None:
        """Soft-invalidate all tokens in a family."""
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.family_id == family_id)
        )
        for row in result.scalars():
            if self._cache:
                await self._cache.delete_key(cache_key(row.token))
            row.used = True
            self._session.add(row)

    async def revoke(self, token: str) -> None:
        """Revoke a refresh token and its entire rotation family."""
        hashed = hash_token(token)
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token == hashed)
        )
        refresh = result.scalar_one_or_none()
        if refresh:
            await self._revoke_family(refresh.family_id)

    async def revoke_by_family(self, family_id: UUID) -> None:
        """Revoke a specific token family."""
        await self._revoke_family(family_id)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoke all token families for a user."""
        result = await self._session.execute(
            select(RefreshToken.family_id)
            .where(
                (RefreshToken.user_id == user_id) | (RefreshToken.tenant_id == user_id)
            )
            .distinct()
        )
        for family_id in result.scalars():
            await self._revoke_family(family_id)

    async def cleanup_expired(
        self,
    ) -> int:
        """Delete all expired and used refresh tokens. Returns count deleted."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(RefreshToken).where(
                (RefreshToken.expires_at < now) | (RefreshToken.used.is_(True))
            )
        )
        token_list = result.scalars().all()
        for t in token_list:
            if self._cache:
                await self._cache.delete_key(cache_key(t.token))
            await self._session.delete(t)
        return len(token_list)

    async def validate(
        self,
        token: str,
        client_meta: ClientMetadata | None = None,
    ) -> tuple[UserIdentity | None, str | None, UUID | None]:
        hashed = hash_token(token)

        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token == hashed)
        )
        refresh = result.scalar_one_or_none()

        if not refresh:
            return None, None, None

        now = datetime.now(timezone.utc)

        if refresh.used:
            await self._revoke_family(refresh.family_id)
            return None, None, None

        refresh_expires_at = (
            refresh.expires_at.replace(tzinfo=timezone.utc)
            if refresh.expires_at.tzinfo is None
            else refresh.expires_at
        )
        if refresh_expires_at < now:
            await self._session.delete(refresh)
            return None, None, None

        if client_meta:
            refresh.ip_address = client_meta.ip_address or refresh.ip_address
            refresh.user_agent = client_meta.user_agent or refresh.user_agent
            self._session.add(refresh)

        if refresh.user_id:
            user_result = await self._session.execute(
                select(User).where(User.id == refresh.user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user or not user.is_active:
                return None, None, None
            user_identity = UserIdentity(
                id=user.id,
                email=EmailAddress(user.email),
                name=user.name,
                picture=HttpsUrl(str(user.picture)) if user.picture else None,
                is_verified=user.is_verified,
                role=user.role,
                project_id=user.project_id,
            )
        else:
            from src.modules.superadmin.infrastructure.models import Tenant

            tenant_result = await self._session.execute(
                select(Tenant).where(Tenant.id == refresh.tenant_id)
            )
            tenant = tenant_result.scalar_one_or_none()
            if not tenant or not tenant.is_active:
                return None, None, None
            user_identity = UserIdentity(
                id=tenant.id,
                email=EmailAddress(tenant.email),
                name=tenant.name,
                picture=HttpsUrl(str(tenant.picture)) if tenant.picture else None,
                is_verified=tenant.is_verified,
                role=tenant.role,
                project_id=None,
            )

        total_lifetime = timedelta(days=self._lifetime_days)
        time_remaining = refresh_expires_at - now
        threshold = total_lifetime * 0.3

        new_token = None
        if time_remaining <= threshold:
            refresh.used = True
            self._session.add(refresh)
            await self._session.flush()

            if self._cache:
                await self._cache.delete_key(cache_key(hashed))
            new_token = await self.create(
                cast(UUID, refresh.user_id or refresh.tenant_id),
                family_id=refresh.family_id,
                auth_provider=refresh.auth_provider,
                client_meta=client_meta,
            )

        return user_identity, new_token, refresh.family_id

    async def get_active_sessions(
        self, user_id: UUID, current_token: str | None = None
    ) -> list[ActiveSession]:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(RefreshToken)
            .where(
                (RefreshToken.user_id == user_id) | (RefreshToken.tenant_id == user_id)
            )
            .where(RefreshToken.used.is_(False))
            .where(RefreshToken.expires_at > now)
        )
        sessions = []
        hashed_current = hash_token(current_token) if current_token else None
        for row in result.scalars():
            is_current = row.token == hashed_current
            sessions.append(
                ActiveSession(
                    family_id=row.family_id,
                    ip_address=row.ip_address,
                    user_agent=row.user_agent,
                    created_at=row.created_at,
                    last_active=row.updated_at,
                    is_current=is_current,
                    auth_provider=row.auth_provider,
                )
            )
        return sessions
