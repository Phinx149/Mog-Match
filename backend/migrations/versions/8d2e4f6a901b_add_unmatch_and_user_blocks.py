"""Add preserved unmatched conversations and user blocks.

Revision ID: 8d2e4f6a901b
Revises: 3af62b02e5c3
"""
from alembic import op
import sqlalchemy as sa

revision = "8d2e4f6a901b"
down_revision = "3af62b02e5c3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("invites") as batch:
        batch.add_column(sa.Column("unmatched_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table("user_blocks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("blocker_id", sa.Uuid(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("blocked_id", sa.Uuid(), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("blocker_id", "blocked_id"),
        sa.CheckConstraint("blocker_id <> blocked_id", name="ck_user_blocks_not_self"))
    op.create_index("ix_user_blocks_blocker_id", "user_blocks", ["blocker_id"])
    op.create_index("ix_user_blocks_blocked_id", "user_blocks", ["blocked_id"])


def downgrade():
    op.drop_table("user_blocks")
    with op.batch_alter_table("invites") as batch:
        batch.drop_column("unmatched_at")
