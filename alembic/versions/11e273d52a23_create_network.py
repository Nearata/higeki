"""create network

Revision ID: 11e273d52a23
Revises:
Create Date: 2025-07-07 17:55:32.677317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import CIDR


# revision identifiers, used by Alembic.
revision: str = '11e273d52a23'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "network",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cidr", CIDR, index=True),
        sa.Column("hiding", sa.Boolean)
    )


def downgrade() -> None:
    op.drop_table("network")
