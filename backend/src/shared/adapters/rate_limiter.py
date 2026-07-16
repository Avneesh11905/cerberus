import time

from src.shared.application.ports.cache import CachePort


class RedisRateLimiter:
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
        Token bucket algorithm.
        Returns (is_allowed, remaining, reset_time)
        We can simulate Token Bucket using a simple fixed window or sliding window,
        or just an incrementing counter with TTL for simplicity, if continuous refill isn't strictly needed for all.
        For continuous refill (leak rate), we can use a more advanced token bucket in Redis.
        Let's implement a simple fixed window counter for now, as it's typically sufficient unless
        token bucket is strictly required. Wait, the plan explicitly says "Token Bucket algorithm".

        Token Bucket using Redis:
        We store a dict: {"tokens": int, "last_refill": float}
        """
        now = time.time()
        # refill rate: tokens per second
        rate = limit / window

        data = await self.cache.get_dict(bucket_key)
        if not data:
            data = {"tokens": limit, "last_refill": now}

        tokens = float(data["tokens"])
        last_refill = float(data["last_refill"])

        # Refill
        elapsed = now - last_refill
        new_tokens = min(limit, tokens + (elapsed * rate))

        if new_tokens >= 1:
            # Allow
            new_tokens -= 1
            await self.cache.set_dict(
                bucket_key, {"tokens": new_tokens, "last_refill": now}, ttl=window
            )
            return True, int(new_tokens), int(now + (1.0 / rate))
        else:
            # Deny
            # When will 1 token be available?
            wait_time = (1.0 - new_tokens) / rate
            reset_time = int(now + wait_time)
            # Update last_refill so we don't lose the fractional tokens
            await self.cache.set_dict(
                bucket_key, {"tokens": new_tokens, "last_refill": now}, ttl=window
            )
            return False, 0, reset_time

    async def is_captcha_cleared(self, key: str) -> bool:
        val = await self.cache.get_string(f"captcha_cleared:{key}")
        return val == "1"

    async def get_failure_count(self, key: str) -> int:
        val = await self.cache.get_string(f"ratelimit:fail:{key}")
        return int(val) if val else 0
