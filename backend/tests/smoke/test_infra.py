import pytest

from src.core.config import get_settings


@pytest.mark.smoke
@pytest.mark.sanity
def test_infra_containers_are_up(infra_containers):
    """
    Smoke test to verify that the test infrastructure (Postgres & Redis)
    spins up properly and the config is correctly patched.
    """
    assert infra_containers["pg_url_asyncpg"] is not None
    assert infra_containers["redis_base"] is not None

    # Assert that pydantic settings were patched
    assert get_settings().database.PGSQL_URL == infra_containers["pg_url_asyncpg"]
    assert get_settings().database.CACHE_URL == f"{infra_containers['redis_base']}/0"
