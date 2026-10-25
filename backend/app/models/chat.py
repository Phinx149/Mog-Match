import uuid

from ..extensions import db
from .base import TimestampMixin


class ChatMessage(TimestampMixin, db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    invite_id = db.Column(db.Uuid, db.ForeignKey("invites.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    client_token = db.Column(db.String(36), nullable=False)
    body = db.Column(db.Text, nullable=False)
    __table_args__ = (db.UniqueConstraint("invite_id", "sender_id", "client_token"),)

    invite = db.relationship("Invite", back_populates="messages")
    sender = db.relationship("Profile", back_populates="messages_sent")


class ProjectIdea(TimestampMixin, db.Model):
    __tablename__ = "project_ideas"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    invite_id = db.Column(db.Uuid, db.ForeignKey("invites.id", ondelete="CASCADE"), nullable=False, index=True)
    generated_by = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    brief = db.Column(db.String(1000), nullable=False, default="")
    content = db.Column(db.JSON, nullable=False)
    context_message_id = db.Column(db.Integer, nullable=True)
    model = db.Column(db.String(100), nullable=False)
    parent_idea_id = db.Column(db.Uuid, db.ForeignKey("project_ideas.id", ondelete="SET NULL",
                                                   name="fk_project_ideas_parent_idea_id"), nullable=True)

    invite = db.relationship("Invite", back_populates="ideas")
    author = db.relationship("Profile", back_populates="ideas_generated")
    studio_turns = db.relationship("StudioTurn", foreign_keys="StudioTurn.idea_id",
                                   back_populates="idea", cascade="all, delete-orphan")


class StudioTurn(TimestampMixin, db.Model):
    """One question/answer pair, optionally holding an unapplied document revision."""

    __tablename__ = "studio_turns"

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Uuid, db.ForeignKey("project_ideas.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    client_token = db.Column(db.String(36), nullable=False)
    mode = db.Column(db.String(10), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    proposal = db.Column(db.JSON, nullable=True)
    change_summary = db.Column(db.JSON, nullable=False, default=list)
    model = db.Column(db.String(100), nullable=False)
    context_message_id = db.Column(db.Integer, nullable=True)
    saved_idea_id = db.Column(db.Uuid, db.ForeignKey("project_ideas.id", ondelete="SET NULL"), nullable=True)
    __table_args__ = (db.UniqueConstraint("idea_id", "author_id", "client_token"),)

    idea = db.relationship("ProjectIdea", foreign_keys=[idea_id], back_populates="studio_turns")
    author = db.relationship("Profile", back_populates="studio_turns")
