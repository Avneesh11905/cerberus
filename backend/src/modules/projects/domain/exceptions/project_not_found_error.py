from .project_error import ProjectError


class ProjectNotFoundError(ProjectError):
    """Raised when a project is not found."""

    pass
