import pytest
from alembic.config import Config

from alembic import command


@pytest.fixture
def alembic_config(infra_containers):
    # We need a psycopg2 URL for Alembic sync operations
    pg_url_asyncpg = infra_containers["pg_url_asyncpg"]
    pg_url_psycopg = pg_url_asyncpg.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", pg_url_psycopg)
    return alembic_cfg


def test_alembic_downgrade_upgrade(alembic_config):
    """
    Test that we can safely downgrade by 1 revision and upgrade back to head.
    Since conftest.py already upgraded to head, we downgrade first.
    """
    # Downgrade by 1
    command.downgrade(alembic_config, "-1")

    # Upgrade back to head
    command.upgrade(alembic_config, "head")


def test_alembic_upgrade_downgrade_base(alembic_config):
    """
    Test a full downgrade to base and upgrade back to head.
    This ensures all migration scripts have correct up/down logic.
    """
    # Downgrade to base
    command.downgrade(alembic_config, "base")

    # Upgrade to head
    command.upgrade(alembic_config, "head")
