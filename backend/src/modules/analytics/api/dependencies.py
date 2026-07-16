from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select

from src.core.container import app_container
from src.modules.analytics.application.use_cases.query_analytics import (
    QueryAnalyticsUseCase,
)
from src.modules.auth.api.dependencies import get_current_user
from src.modules.auth.domain import UserIdentity
from src.modules.projects.infrastructure.models import Project
from src.shared.adapters.uow import SQLAlchemyUnitOfWork, get_uow
from src.shared.domain.enums import UserRole


def get_query_analytics_use_case() -> QueryAnalyticsUseCase:
    return QueryAnalyticsUseCase(repository=app_container.analytics_repo)


async def verify_project_ownership(
    project_id: UUID,
    user: Annotated[UserIdentity, Depends(get_current_user)],
    uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)],
) -> None:
    """Verifies that the current user's tenant owns the requested project, or the user is a superadmin."""
    if user.role == UserRole.SUPERADMIN:
        return

    async with uow:
        result = await uow.session.execute(
            select(Project.tenant_id).where(Project.id == project_id)
        )
        tenant_id = result.scalar_one_or_none()

        if not tenant_id:
            raise HTTPException(status_code=404, detail="Project not found")

        if tenant_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
