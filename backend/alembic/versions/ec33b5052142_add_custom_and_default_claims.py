"""add custom and default claims

Revision ID: ec33b5052142
Revises: 4c666f09c1d3
Create Date: 2026-07-19 02:16:49.693773

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "ec33b5052142"
down_revision: Union[str, Sequence[str], None] = "4c666f09c1d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "projects",
        sa.Column("default_claims", JSONB(), server_default="{}", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("custom_claims", JSONB(), server_default="{}", nullable=False),
    )
    op.create_index(
        "idx_users_custom_claims_gin",
        "users",
        ["custom_claims"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_users_custom_claims_gin", table_name="users", postgresql_using="gin"
    )
    op.drop_column("users", "custom_claims")
    op.drop_column("projects", "default_claims")
