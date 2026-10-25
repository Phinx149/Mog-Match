"""merge chat studio and profile theme migrations

Revision ID: 7b09b0192ba5
Revises: ec17fb96ac46, cb2510bf61da
Create Date: 2026-10-24 22:58:59.577712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b09b0192ba5'
down_revision = ('ec17fb96ac46', 'cb2510bf61da')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
