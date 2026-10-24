"""Store uploaded profile photos on users."""
from alembic import op
import sqlalchemy as sa

revision = "a12b34c56def"
down_revision = "440781ed943a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("photo_data", sa.LargeBinary(), nullable=True))
    op.add_column("users", sa.Column("photo_mimetype", sa.String(40), nullable=True))


def downgrade():
    op.drop_column("users", "photo_mimetype")
    op.drop_column("users", "photo_data")
