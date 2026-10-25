import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

# Vercel sets VERCEL=1 in deployed functions (and in `vercel dev`).
ON_VERCEL = os.getenv("VERCEL") == "1"
DEFAULT_SECRET_KEY = "dev-only-not-secret"


def normalize_database_url(url: str) -> str:
    """Make a hosting provider's Postgres URL usable by SQLAlchemy with the psycopg (v3) driver."""
    # Some hosts hand out "postgres://", which SQLAlchemy no longer accepts.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    # A bare "postgresql://" makes SQLAlchemy look for psycopg2, which we don't install.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def _database_url() -> str | None:
    # DATABASE_URL is ours; POSTGRES_URL is what Vercel's Postgres integrations (Neon) also set.
    url = (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "").strip()
    if not url:
        return None  # create_app falls back to SQLite in the instance folder (local dev only)
    return normalize_database_url(url)


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Hosted Postgres (and serverless functions that sleep) drop idle connections:
        # test each one before use and replace connections older than 5 minutes.
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
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
    # Required (and checked in create_app) on Vercel; the default is for your laptop only.
    SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True  # page JavaScript can't read the cookie
    SESSION_COOKIE_SECURE = ON_VERCEL  # HTTPS-only cookie when deployed
    # Every seeded user gets this password (demo data). Use a different one when seeding production.
    SEED_PASSWORD = os.getenv("SEED_PASSWORD", "mogmatch-demo")
    # Vercel rejects request bodies over 4.5 MB, so keep uploads (plus form overhead) under that.
    MAX_PHOTO_BYTES = 4 * 1024 * 1024
    ON_VERCEL = ON_VERCEL
