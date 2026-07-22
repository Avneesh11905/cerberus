from .superadmin_base_exception import SuperadminBaseException


class AbsoluteSuperadminImmutableException(SuperadminBaseException):
    """The absolute superadmin role is immutable and cannot be modified."""

    pass
