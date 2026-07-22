from .project_error import ProjectError


class ProjectForbiddenError(ProjectError):
    """Raised when access to a project is forbidden."""

    pass
