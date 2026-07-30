import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.config.app import CoreSettings
from src.core.config.auth import RateLimitSettings
from src.shared.application.ports import AnalyticsEventPort, RateLimiterPort, CachePort
from src.shared.infrastructure.adapters.logger import AsyncSQLLogger

logger = AsyncSQLLogger(__name__)


def parse_rate(rate_str: str) -> tuple[int, int]:
    try:
        count_str, period_str = rate_str.split("/")
        count = int(count_str)
        period = period_str.lower()
        if period in ("second", "s"):
            window = 1
        elif period in ("minute", "m"):
            window = 60
        elif period in ("hour", "h"):
            window = 3600
        elif period in ("day", "d"):
            window = 86400
        else:
            window = 60
        return count, window
    except Exception:
        return 60, 60


class RateLimitAndAnalyticsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        core_settings: CoreSettings,
        rate_limit_settings: RateLimitSettings,
        rate_limiter: RateLimiterPort,
        analytics: AnalyticsEventPort,
        cache: CachePort,
        default_rate: str = "60/minute",
        auth_rate: str = "10/minute",
    ):
        super().__init__(app)
        self.core_settings = core_settings
        self.rate_limit_settings = rate_limit_settings
        self.rate_limiter = rate_limiter
        self.analytics = analytics
        self.cache = cache

        self.default_count, self.default_window = parse_rate(default_rate)
        self.auth_count, self.auth_window = parse_rate(auth_rate)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request.state.is_challenged = False

        ip = request.client.host if request.client else "127.0.0.1"
        if "cf-connecting-ip" in request.headers:
            ip = request.headers["cf-connecting-ip"]
        elif "x-forwarded-for" in request.headers:
            ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        if not self.rate_limit_settings.ENABLED:
            response = await call_next(request)
            self._emit_api_request(request, response, start_time, ip)
            return response

        path = request.url.path
        is_auth_route = "/auth/" in path

        project_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                import jwt

                payload = jwt.decode(token, options={"verify_signature": False})
                project_id = payload.get("project_id")
            except Exception as e:
                await logger.debug(
                    f"Failed to decode JWT for rate limit project extraction: {e}"
                )
        else:
            api_key = request.headers.get("x-cerberus-api-key")
            if api_key:
                try:
                    import hashlib

                    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                    cache_key = f"api_key_hash:{key_hash}"
                    project_id = await self.cache.get_string(cache_key)
                except Exception as e:
                    await logger.error(f"Failed to fetch API key hash from cache: {e}")

        if project_id and getattr(request.app.state, "project_environments", None):
            env = request.app.state.project_environments.get(str(project_id))
            if env == "development":
                response = await call_next(request)
                self._emit_api_request(request, response, start_time, ip)
                return response

        limit = self.auth_count if is_auth_route else self.default_count
        window = self.auth_window if is_auth_route else self.default_window
        bucket_key = f"ratelimit:ip:{ip}"

        is_allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
            bucket_key, limit, window
        )

        if not is_allowed:
            if is_auth_route:
                # For auth routes, we escalate to a CAPTCHA challenge instead of outright blocking
                request.state.is_challenged = True
            else:
                # For regular API routes, block with 429
                headers = {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time())),
                }
                detail = "Too many requests. Please try again later."
                if self.core_settings.ENV == "development":
                    detail = f"Rate limit exceeded. Try again in {reset_time - int(time.time())}s"

                return JSONResponse(
                    status_code=429,
                    content={"detail": detail},
                    headers=headers,
                )

        response = await call_next(request)

        if hasattr(response, "headers"):
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)

        self._emit_api_request(request, response, start_time, ip)
        return response

    def _emit_api_request(self, request: Request, response, start_time: float, ip: str):
        path = request.url.path
        if (
            path in ("/health", "/metrics", "/favicon.ico")
            or path.startswith("/docs")
            or path.startswith("/redoc")
            or path.startswith("/openapi.json")
        ):
            return

        duration = time.time() - start_time

        metadata = {
            "path": path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000),
            "ip_address": ip,
            "user_agent": request.headers.get("user-agent", ""),
        }

        self.analytics.record_event(event_type="API_REQUEST", metadata=metadata)
