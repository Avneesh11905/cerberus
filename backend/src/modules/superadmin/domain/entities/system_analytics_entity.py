from .platform_adoption_metrics import PlatformAdoptionMetrics
from .end_user_usage_metrics import EndUserUsageMetrics
from dataclasses import dataclass


@dataclass(kw_only=True)
class SystemAnalyticsEntity:
    platform_adoption: PlatformAdoptionMetrics
    end_user_usage: EndUserUsageMetrics
