from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GetSystemAnalyticsQuery:
    pass


@dataclass(frozen=True)
class ListTenantsQuery:
    skip: int = 0
    limit: int = 20
    search: Optional[str] = None


@dataclass(frozen=True)
class ListTenantLogsQuery:
    skip: int = 0
    limit: int = 50
    level: Optional[str] = None
