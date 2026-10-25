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
    # The seeded user the app is demoed as. Logging in is what makes "me" = a user.
    DEMO_USER_EMAIL = os.getenv("DEMO_USER_EMAIL", "demo@mogmatch.dev")
    # Signs the login cookie so the browser can't change who it's logged in as.
    # Set a long random value in .env anywhere other than your own laptop.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-not-secret")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True  # page JavaScript can't read the cookie
    # Every seeded user gets this password (local demo data only).
    SEED_PASSWORD = os.getenv("SEED_PASSWORD", "mogmatch-demo")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
