import uuid

from ..extensions import db
from .base import TimestampMixin


class UserBlock(TimestampMixin, db.Model):
    __tablename__ = "user_blocks"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    blocker_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    blocked_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint("blocker_id", "blocked_id"),
                      db.CheckConstraint("blocker_id <> blocked_id", name="ck_user_blocks_not_self"))
