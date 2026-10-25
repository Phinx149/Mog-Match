import uuid

from ..extensions import db
from .base import TimestampMixin


class Profile(TimestampMixin, db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(
        db.Uuid, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(40), nullable=False, unique=True, index=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    education = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=False, default="")
    favorite_ide = db.Column(db.String(80), nullable=True)
    experience_level = db.Column(db.String(40), nullable=True)

    # List-valued fields are JSON arrays of strings. Programming languages live in `skills`.
    skills = db.Column(db.JSON, nullable=False, default=list)
    interests = db.Column(db.JSON, nullable=False, default=list)
    favorite_ai_agents = db.Column(db.JSON, nullable=False, default=list)
    looking_for = db.Column(db.JSON, nullable=False, default=list)

    # Cosmetic preferences for how this profile's card/page looks, e.g. {"background": "#172554"}.
    # NULL = default look. A JSON object (not one column per option) so new options don't need
    # a migration each. Assign a new dict when updating, like the list columns above.
    theme = db.Column(db.JSON, nullable=True)

    user = db.relationship("User", back_populates="profile")
    links = db.relationship(
        "ProfileLink",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="ProfileLink.position",
    )
    projects = db.relationship(
        "Project",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Project.position",
    )
    # Deleting a profile removes its swipes and invites in both directions (SQLite doesn't enforce
    # ON DELETE CASCADE by default, so the ORM does it).
    swipes_made = db.relationship(
        "Swipe", foreign_keys="Swipe.swiper_id", back_populates="swiper", cascade="all, delete-orphan"
    )
    swipes_received = db.relationship(
        "Swipe", foreign_keys="Swipe.target_id", back_populates="target", cascade="all, delete-orphan"
    )
    invites_sent = db.relationship(
        "Invite", foreign_keys="Invite.sender_id", back_populates="sender", cascade="all, delete-orphan"
    )
    invites_received = db.relationship(
        "Invite", foreign_keys="Invite.recipient_id", back_populates="recipient", cascade="all, delete-orphan"
    )
    messages_sent = db.relationship("ChatMessage", back_populates="sender", cascade="all, delete-orphan")
    ideas_generated = db.relationship("ProjectIdea", back_populates="author", cascade="all, delete-orphan")
    studio_turns = db.relationship("StudioTurn", back_populates="author", cascade="all, delete-orphan")
    blocks_made = db.relationship("UserBlock", foreign_keys="UserBlock.blocker_id", cascade="all, delete-orphan")
    blocks_received = db.relationship("UserBlock", foreign_keys="UserBlock.blocked_id", cascade="all, delete-orphan")


class ProfileLink(db.Model):
    __tablename__ = "profile_links"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    profile_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    label = db.Column(db.String(40), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)

    profile = db.relationship("Profile", back_populates="links")
