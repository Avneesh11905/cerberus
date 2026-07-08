"""
Exposes liveness and readiness probes for orchestrators (like Kubernetes or Docker Compose).
Checks connectivity to the PostgreSQL database and Redis cache to ensure the application is healthy.
"""

from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi import Response
from sqlalchemy import text

from src.shared.config import database_settings
from src.shared.infrastructure.sql.uow import SQLAlchemyUnitOfWork, get_uow

router = APIRouter()


class HealthComponents(BaseModel):
    database: str
    cache: str


class HealthResponse(BaseModel):
    status: str
    components: HealthComponents


@router.get("/health", response_model=HealthResponse)
async def health_check(
    response: Response, uow: Annotated[SQLAlchemyUnitOfWork, Depends(get_uow)]
):
    # Check DB
    try:
        async with uow:
            await uow.session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Check Redis/Cache
    cache_status = "ok"
    if database_settings.CACHE_URL.startswith("redis"):
        client = redis.from_url(database_settings.CACHE_URL)
        try:
            await client.ping()
            cache_status = "ok"
        except Exception:
            cache_status = "error"
        finally:
            #  Always close the client to prevent connection leaks under frequent probes.
            await client.aclose()

    status_str = "ok" if db_status == "ok" and cache_status == "ok" else "degraded"

    if status_str != "ok":
        response.status_code = 503

    return HealthResponse(
        status=status_str,
        components=HealthComponents(database=db_status, cache=cache_status),
    )
