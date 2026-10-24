import uuid

from ..extensions import db
from .base import TimestampMixin


class Project(TimestampMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    profile_id = db.Column(
        db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    project_url = db.Column(db.String(500), nullable=True)
    technologies = db.Column(db.JSON, nullable=False, default=list)
    position = db.Column(db.Integer, nullable=False, default=0)

    profile = db.relationship("Profile", back_populates="projects")
