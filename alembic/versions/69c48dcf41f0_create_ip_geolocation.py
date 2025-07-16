"""create ipgeolocation

Revision ID: 69c48dcf41f0
Revises: 8f1d08fe3ca4
Create Date: 2025-07-11 14:28:57.476149

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "69c48dcf41f0"
down_revision: Union[str, Sequence[str], None] = "8f1d08fe3ca4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipgeolocation",
        sa.Column("network_id", sa.Integer, sa.ForeignKey("network.id"), primary_key=True, index=True),
        sa.Column("city", sa.String),
        sa.Column("state", sa.String),
        sa.Column("country", sa.String),
        sa.Column("flag", sa.String),
        sa.Column("postal", sa.String),
        sa.Column("timezone", sa.String),
        sa.Column("coordinates", sa.String),
    )


def downgrade() -> None:
    op.drop_table("ipgeolocation")
