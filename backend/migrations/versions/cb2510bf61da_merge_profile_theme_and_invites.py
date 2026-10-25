"""merge profile theme and invites

Revision ID: cb2510bf61da
Revises: 7aa0f0ec4b7d, bfee4bc279da
Create Date: 2026-10-24 22:27:25.965534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb2510bf61da'
down_revision = ('7aa0f0ec4b7d', 'bfee4bc279da')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
