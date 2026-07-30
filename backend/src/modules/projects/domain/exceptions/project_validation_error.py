from .project_error import ProjectError


class ProjectValidationError(ProjectError):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("Validation failed.")
