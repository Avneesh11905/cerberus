class SuperadminBaseException(Exception):
    """Base exception for the superadmin domain."""

    pass


class TenantNotFoundException(SuperadminBaseException):
    pass


class AbsoluteSuperadminImmutableException(SuperadminBaseException):
    """The absolute superadmin role is immutable and cannot be modified."""
    pass
