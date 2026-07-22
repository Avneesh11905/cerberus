from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class GetProjectMetricsQuery:
    project_id: UUID
    start_date: date
    end_date: date


@dataclass(frozen=True)
class GetTenantMetricsQuery:
    tenant_id: UUID
    start_date: date
    end_date: date
