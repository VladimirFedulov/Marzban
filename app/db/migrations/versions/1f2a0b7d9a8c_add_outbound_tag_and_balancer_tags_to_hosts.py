"""add outbound tag and balancer tags to hosts

Revision ID: 1f2a0b7d9a8c
Revises: fe7796f840a4
Create Date: 2025-01-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1f2a0b7d9a8c'
down_revision = 'c1f6e2b6b2f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('hosts') as batch_op:
        batch_op.add_column(sa.Column('outbound_tag', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('balancer_tags', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('hosts') as batch_op:
        batch_op.drop_column('balancer_tags')
        batch_op.drop_column('outbound_tag')
