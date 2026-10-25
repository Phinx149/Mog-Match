import os

import pytest

from app import create_app
from app.config import normalize_database_url
from app.extensions import db
from app.seed import seed_database


@pytest.fixture
def app(tmp_path):
    # Default: a throwaway SQLite file. Set TEST_DATABASE_URL to run the same tests on Postgres,
    # e.g. TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/mogmatch_test pytest
    # (every table in that database is dropped and recreated, so never point it at real data).
    url = os.getenv("TEST_DATABASE_URL")
    url = normalize_database_url(url) if url else f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": url})
    with app.app_context():
        db.drop_all()  # Postgres keeps tables between runs; start clean
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()  # release the file so Windows can delete tmp_path


@pytest.fixture
def log_in(app):
    """log_in(client, username) logs that test client in as a seeded user."""

    def _log_in(client, username="jordan-dev"):
        password = app.config["SEED_PASSWORD"]
        response = client.post("/api/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200, response.get_json()
        return client

    return _log_in


@pytest.fixture
def anon_client(app):
    """Nobody logged in."""
    return app.test_client()


@pytest.fixture
def client(app, log_in):
    """Logged in as the demo user, Jordan (most tests act as "me")."""
    return log_in(app.test_client())
