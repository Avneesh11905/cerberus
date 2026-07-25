from dataclasses import dataclass
from pydantic import JsonValue


@dataclass(frozen=True)
class ProjectMetricsDTO:
    data: list[dict[str, JsonValue]]


@dataclass(frozen=True)
class TenantMetricsDTO:
    data: list[dict[str, JsonValue]]
