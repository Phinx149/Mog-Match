import uuid

from ..extensions import db
from .base import TimestampMixin


class Invite(TimestampMixin, db.Model):
    """A request to connect, sent to someone I liked. The recipient sees it in their inbox."""

    __tablename__ = "invites"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    sender_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message = db.Column(db.String(280), nullable=True)
    # "pending" | "accepted" | "declined", validated in invite_service
    status = db.Column(db.String(10), nullable=False, default="pending")

    # One invite per direction: inviting the same person twice is a 409, not a second row.
    __table_args__ = (db.UniqueConstraint("sender_id", "recipient_id"),)

    sender = db.relationship("Profile", foreign_keys=[sender_id], back_populates="invites_sent")
    recipient = db.relationship(
        "Profile", foreign_keys=[recipient_id], back_populates="invites_received"
    )
