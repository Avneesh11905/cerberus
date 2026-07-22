from pydantic import BaseModel, ConfigDict


class AnalyticsMetrics(BaseModel):
    total_tenants: int = 0
    total_projects: int = 0
    api_requests: int = 0
    registrations: int = 0
    login_successes: int = 0
    login_failures: int = 0
    active_users: int = 0
    model_config = ConfigDict(from_attributes=True)
