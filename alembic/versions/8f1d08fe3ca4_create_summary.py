"""create summary

Revision ID: 8f1d08fe3ca4
Revises: 11e273d52a23
Create Date: 2025-07-10 15:31:58.221278

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import CIDR

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f1d08fe3ca4"
down_revision: Union[str, Sequence[str], None] = "11e273d52a23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "summary",
        sa.Column("network_id", sa.Integer, sa.ForeignKey("network.id"), primary_key=True, index=True),
        sa.Column("asn", sa.String),
        sa.Column("hostname", sa.String(255)),
        sa.Column("cidr", CIDR, index=True),
        sa.Column("company", sa.String),
        sa.Column("hosted_domains", sa.Integer),
        sa.Column("privacy", sa.Boolean),
        sa.Column("anycast", sa.Boolean),
        sa.Column("asn_type", sa.String),
        sa.Column("abuse_contact", sa.String),
    )


def downgrade() -> None:
    op.drop_table("summary")
