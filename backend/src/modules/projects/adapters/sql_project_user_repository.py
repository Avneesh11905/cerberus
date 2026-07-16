"""
Executes database queries for project user management using SQLAlchemy.
Maps raw database rows into pure `UserProfile` domain entities.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.users.domain import UserProfile
from src.modules.users.infrastructure.models import User
from src.shared.domain.enums import UserRole


class SQLProjectUserRepository:
    """Implements ProjectUserRepositoryPort using SQLAlchemy."""

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

    async def list_project_users(
        self,
        session: AsyncSession,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[UserProfile]:
        stmt = (
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.project_id == project_id)
        )

        if search:
            stmt = stmt.where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%"),
                    User.role.cast(str).ilike(f"%{search}%"),
                )
            )

        stmt = stmt.order_by(User.email.asc()).offset(skip).limit(limit)

        result = await session.execute(stmt)
        users = result.scalars().all()

        return [self._to_profile(u) for u in users]

    async def count_project_users(
        self, session: AsyncSession, project_id: UUID, search: str | None = None
    ) -> int:
        stmt = select(func.count(User.id)).where(User.project_id == project_id)

        if search:
            stmt = stmt.where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%"),
                    User.role.cast(str).ilike(f"%{search}%"),
                )
            )

        result = await session.execute(stmt)
        return result.scalar_one() or 0

    async def update_user_role(
        self, session: AsyncSession, project_id: UUID, user_id: UUID, new_role: UserRole
    ) -> UserProfile | None:
        result = await session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id, User.project_id == project_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.role = new_role
        await session.flush()

        return self._to_profile(user)

    async def update_user_status(
        self, session: AsyncSession, project_id: UUID, user_id: UUID, is_active: bool
    ) -> UserProfile | None:
        result = await session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id, User.project_id == project_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = is_active
        await session.flush()

        return self._to_profile(user)

    async def update_tenant_user_status(
        self, session: AsyncSession, tenant_id: UUID, email: str, is_active: bool
    ) -> list[UserProfile]:
        from src.modules.projects.infrastructure.models import Project

        result = await session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .join(Project, User.project_id == Project.id)
            .where(User.email == email, Project.tenant_id == tenant_id)
        )
        users = result.scalars().all()

        if not users:
            return []

        for user in users:
            user.is_active = is_active

        await session.flush()
        return [self._to_profile(u) for u in users]
