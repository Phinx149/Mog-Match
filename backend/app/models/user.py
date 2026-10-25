import uuid

from ..extensions import db
from .base import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=True)
    # A salted hash (werkzeug.security), never the password itself. Null = can't log in.
    password_hash = db.Column(db.String(255), nullable=True)
    photo_data = db.Column(db.LargeBinary, nullable=True)
    photo_mimetype = db.Column(db.String(40), nullable=True)

    profile = db.relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
