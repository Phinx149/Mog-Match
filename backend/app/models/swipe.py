import uuid

from ..extensions import db
from .base import TimestampMixin


class Swipe(TimestampMixin, db.Model):
    """One profile's like/pass on another. Two likes in opposite directions = a match."""

    __tablename__ = "swipes"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    swiper_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action = db.Column(db.String(10), nullable=False)  # "like" | "pass", validated in swipe_service

    # You swipe on someone once; swiping again updates this row instead of adding another.
    __table_args__ = (db.UniqueConstraint("swiper_id", "target_id"),)

    swiper = db.relationship("Profile", foreign_keys=[swiper_id], back_populates="swipes_made")
    target = db.relationship("Profile", foreign_keys=[target_id], back_populates="swipes_received")
