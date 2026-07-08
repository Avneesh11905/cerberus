"""
Executes database queries for user profiles using SQLAlchemy.
Maps raw database rows into pure `UserProfile` domain entities to prevent ORM leakage.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.shared.infrastructure.sql.tables import User
from src.users.core.domain import UserProfile
from src.users.core.domain.exceptions import UserNotFoundException


from src.authentication.core.ports import RefreshTokenRepositoryPort

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
            id=str(user.id),
            email=user.email,
            role=user.role,
            project_id=str(user.project_id) if user.project_id else None,
            name=user.name,
            picture=user.picture,
            receive_updates=user.receive_updates,
            login_methods=methods
        )

    async def get_profile(self, session: AsyncSession, user_id: UUID) -> UserProfile | None:
        result = await session.execute(select(User).options(selectinload(User.oauth_accounts)).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        return self._to_profile(user)

    async def update_profile(
        self, session: AsyncSession, user_id: UUID, name: str | None = None, picture: str | None = None, receive_updates: bool | None = None
    ) -> UserProfile:
        result = await session.execute(select(User).options(selectinload(User.oauth_accounts)).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        if name is not None:
            user.name = name
        if picture is not None:
            user.picture = picture
        if receive_updates is not None:
            user.receive_updates = receive_updates
        await session.flush()
        return self._to_profile(user)

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> None:
        """Hard delete a user (cascades to projects, oauth, tokens)."""
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await self._refresh_repo.revoke_all_for_user(session, user_id)
            await session.delete(user)
            await session.flush()
