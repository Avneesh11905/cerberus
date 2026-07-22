from .metric_response import MetricResponse

from pydantic import BaseModel


class QueryAnalyticsResponse(BaseModel):
    metrics: list[MetricResponse]
