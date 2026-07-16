from typing import Protocol


class RateLimiterPort(Protocol):
    """
    Port for managing rate limiter state manually from Use Cases.
    Middleware only reads state; Use Cases orchestrate outcomes.
    """

    async def record_success(self, key: str) -> None:
        """
        Record a successful core action, clearing the failure counter and CHALLENGE flag.
        """
        ...

    async def record_failure(self, key: str) -> None:
        """
        Record a failed core action or missing Turnstile token, advancing the failure counter.
        """
        ...

    async def record_captcha_success(self, key: str) -> None:
        """
        Record that Turnstile succeeded but the core action failed, setting a short-lived
        flag so the user doesn't have to re-solve CAPTCHA on every retry.
        """
        ...

    async def check_rate_limit(
        self, bucket_key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        """
        Token bucket algorithm.
        Returns (is_allowed, remaining, reset_time)
        """
