from dataclasses import dataclass


@dataclass(kw_only=True)
class EndUserUsageMetrics:
    total_projects: int
    api_requests: int
    registrations: int
    login_successes: int
    login_failures: int
    active_users: int
