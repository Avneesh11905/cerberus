import time

from src.shared.application.ports import CachePort


class RedisRateLimiterAdapter:
    """
    Custom Redis rate limiter.
    Implements RateLimiterPort for Use Case callbacks.
    Also provides token-bucket logic for the RateLimitAndAnalyticsMiddleware.
    """

    def __init__(self, cache: CachePort):
        self.cache = cache

    async def record_success(self, key: str) -> None:
        await self.cache.delete_key(f"ratelimit:fail:{key}")
        await self.cache.delete_key(f"ratelimit:challenge:{key}")

    async def record_failure(self, key: str) -> None:
        await self.cache.incr(f"ratelimit:fail:{key}", ttl=900)

    async def record_captcha_success(self, key: str) -> None:
        await self.cache.set_string(f"captcha_cleared:{key}", "1", ttl=300)

    async def check_rate_limit(
        self, bucket_key: str, limit: int, window: int
    ) -> tuple[bool, int, int]:
        """
        Simple Fixed Window algorithm using atomic incr.
        Returns (is_allowed, remaining, reset_time)
        """
        now = time.time()
        # Round the timestamp to the nearest window boundary to create buckets
        current_window_start = int(now // window) * window
        key = f"{bucket_key}:{current_window_start}"

        count = await self.cache.incr(key, ttl=window)

        reset_time = current_window_start + window
        remaining = max(0, limit - count)

        is_allowed = count <= limit

        return is_allowed, remaining, reset_time

    async def is_captcha_cleared(self, key: str) -> bool:
        val = await self.cache.get_string(f"captcha_cleared:{key}")
        return val == "1"

    async def get_failure_count(self, key: str) -> int:
        val = await self.cache.get_string(f"ratelimit:fail:{key}")
        return int(val) if val else 0
