"""Add merge_primary to hosts

Revision ID: b9c5f0f2d2d9
Revises: 1f2a0b7d9a8c
Create Date: 2025-09-27 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9c5f0f2d2d9"
down_revision = "1f2a0b7d9a8c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "hosts",
        sa.Column("merge_primary", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.alter_column("hosts", "merge_primary", server_default=None)


def downgrade() -> None:
    op.drop_column("hosts", "merge_primary")
