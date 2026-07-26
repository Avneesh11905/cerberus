from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectMetricsDTO:
    metrics: list
    totals: dict = field(default_factory=dict)


@dataclass(frozen=True)
class TenantMetricsDTO:
    metrics: list
    totals: dict = field(default_factory=dict)
