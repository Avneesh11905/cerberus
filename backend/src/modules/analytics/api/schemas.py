from datetime import date

from pydantic import BaseModel, ConfigDict


class MetricResponse(BaseModel):
    date: date
    api_requests: int
    login_successes: int
    login_failures: int
    registrations: int
    active_users: int

    model_config = ConfigDict(from_attributes=True)


class QueryAnalyticsResponse(BaseModel):
    metrics: list[MetricResponse]
