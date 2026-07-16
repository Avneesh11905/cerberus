class ProjectError(Exception):
    """Base exception for Project domain."""

    pass


class ProjectNotFoundError(ProjectError):
    """Raised when a project is not found."""

    pass


class ProjectForbiddenError(ProjectError):
    """Raised when access to a project is forbidden."""

    pass
