import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


def _database_url() -> str | None:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return None  # create_app falls back to SQLite in the instance folder
    # Some hosts hand out "postgres://", which SQLAlchemy no longer accepts.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    # Until real authentication exists, /api/profiles/me always acts as this user.
    DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@mogmatch.dev")
