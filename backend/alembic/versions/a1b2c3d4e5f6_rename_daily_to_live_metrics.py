"""rename daily_*_metrics tables to live_*_metrics for real-time UPSERT strategy

Revision ID: a1b2c3d4e5f6
Revises: 304e4309fb10
Create Date: 2026-07-26 04:33:00.000000

"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "304e4309fb10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename tables
    op.rename_table("daily_project_metrics", "live_project_metrics")
    op.rename_table("daily_tenant_metrics", "live_tenant_metrics")
    op.rename_table("daily_system_metrics", "live_system_metrics")

    # Rename unique constraints to match new table names
    op.execute(
        "ALTER TABLE live_project_metrics RENAME CONSTRAINT uq_project_date TO uq_live_project_date"
    )
    op.execute(
        "ALTER TABLE live_tenant_metrics RENAME CONSTRAINT uq_tenant_date TO uq_live_tenant_date"
    )
    op.execute(
        "ALTER TABLE live_system_metrics RENAME CONSTRAINT uq_system_date TO uq_live_system_date"
    )


def downgrade() -> None:
    # Revert constraint renames
    op.execute(
        "ALTER TABLE live_project_metrics RENAME CONSTRAINT uq_live_project_date TO uq_project_date"
    )
    op.execute(
        "ALTER TABLE live_tenant_metrics RENAME CONSTRAINT uq_live_tenant_date TO uq_tenant_date"
    )
    op.execute(
        "ALTER TABLE live_system_metrics RENAME CONSTRAINT uq_live_system_date TO uq_system_date"
    )

    # Revert table renames
    op.rename_table("live_project_metrics", "daily_project_metrics")
    op.rename_table("live_tenant_metrics", "daily_tenant_metrics")
    op.rename_table("live_system_metrics", "daily_system_metrics")
