from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ProjectMetricsDTO:
    data: List[Dict[str, Any]]


@dataclass(frozen=True)
class TenantMetricsDTO:
    data: List[Dict[str, Any]]
