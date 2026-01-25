"""add subscription types to hosts

Revision ID: 0b6ef93e6a2c
Revises: fe7796f840a4
Create Date: 2025-02-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0b6ef93e6a2c"
down_revision = "c1f6e2b6b2f4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("hosts", sa.Column("subscription_types", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("hosts", "subscription_types")
