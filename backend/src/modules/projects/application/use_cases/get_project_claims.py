from src.modules.projects.application.use_cases import BaseProjectUseCase


class GetProjectClaimsUseCase[SessionType](BaseProjectUseCase[SessionType]):
    """Retrieves the default custom claims schema for a project."""

    async def execute(self, session: SessionType, project_id, user_id) -> dict:
        project = await self._get_project_or_404(session, project_id, user_id)
        return project.default_claims
