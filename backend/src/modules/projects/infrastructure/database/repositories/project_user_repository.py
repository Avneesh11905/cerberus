"""
Executes database queries for project user management using SQLAlchemy.
Maps raw database rows into pure `UserProfile` domain entities.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.projects.domain.entities.project_user import ProjectUser
from src.modules.users.infrastructure.models import User
from src.shared.domain.value_objects import EmailAddress, HttpsUrl, PersonName


class SQLProjectUserRepositoryAdapter:
    def __init__(self, session: AsyncSession):
        self._session = session

    """Implements ProjectUserRepositoryPort using SQLAlchemy."""

    def _to_profile(self, user: User) -> ProjectUser:
        methods = []
        if user.password:
            methods.append("local")
        for account in user.oauth_accounts:
            methods.append(account.provider)

        return ProjectUser(
            id=user.id,
            email=EmailAddress(user.email),
            role=None,
            project_id=user.project_id,
            name=PersonName(user.name) if user.name else None,
            picture=HttpsUrl(user.picture) if user.picture else None,
            receive_updates=user.receive_updates,
            is_active=user.is_active,
            login_methods=methods,
            custom_claims=user.custom_claims,
        )

    async def list_project_users(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> tuple[Sequence[ProjectUser], int]:
        stmt = (
            select(User, func.count().over().label("total"))
            .options(selectinload(User.oauth_accounts))
            .where(User.project_id == project_id)
        )

        if search:
            stmt = stmt.where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%"),
                )
            )

        stmt = stmt.order_by(User.email.asc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        rows = result.all()

        if not rows:
            return [], 0

        total = rows[0].total
        users = [self._to_profile(row[0]) for row in rows]
        return users, total

    async def update_user_status(
        self, project_id: UUID, user_id: UUID, is_active: bool
    ) -> ProjectUser | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id, User.project_id == project_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = is_active
        await self._session.flush()

        return self._to_profile(user)

    async def update_tenant_user_status(
        self, tenant_id: UUID, email: str, is_active: bool
    ) -> list[ProjectUser]:
        from src.modules.projects.infrastructure.models import Project

        result = await self._session.execute(
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

        await self._session.flush()
        return [self._to_profile(u) for u in users]

    async def update_user_claims(
        self, project_id: UUID, user_id: UUID, overrides: dict
    ) -> ProjectUser | None:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.oauth_accounts))
            .where(User.id == user_id, User.project_id == project_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.custom_claims = overrides
        await self._session.flush()

        return self._to_profile(user)
