"""add hwid device limits

Revision ID: 8f1b5f45f2f9
Revises: 07f9bbb3db4e
Create Date: 2025-02-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f1b5f45f2f9'
down_revision = '07f9bbb3db4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hwid_device_limit', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('hwid_device_limit_enabled', sa.Boolean(), nullable=True))

    op.create_table(
        'user_hwid_devices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('hwid', sa.String(length=128), nullable=False),
        sa.Column('device_os', sa.String(length=64), nullable=True),
        sa.Column('device_model', sa.String(length=128), nullable=True),
        sa.Column('device_os_version', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'hwid', name='uq_user_hwid_devices_user_hwid'),
    )


def downgrade() -> None:
    op.drop_table('user_hwid_devices')
    op.drop_column('users', 'hwid_device_limit_enabled')
    op.drop_column('users', 'hwid_device_limit')
