from .analytics_metrics import AnalyticsMetrics

from pydantic import BaseModel, ConfigDict


class SystemAnalyticsRes(BaseModel):
    platform_adoption: AnalyticsMetrics
    end_user_usage: AnalyticsMetrics
    model_config = ConfigDict(from_attributes=True)
