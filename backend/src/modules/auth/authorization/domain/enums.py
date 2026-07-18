from enum import StrEnum


class GlobalRole(StrEnum):
    SUPERADMIN = "SUPERADMIN"
    TENANT = "TENANT"


class ProjectRole(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"
