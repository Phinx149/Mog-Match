import pytest

from app import create_app
from app.config import normalize_database_url


@pytest.mark.parametrize(
    "given, expected",
    [
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql://u:p@host/db?sslmode=require", "postgresql+psycopg://u:p@host/db?sslmode=require"),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),  # already explicit
        ("sqlite:///local.db", "sqlite:///local.db"),
    ],
)
def test_database_urls_use_the_installed_driver(given, expected):
    assert normalize_database_url(given) == expected


def vercel_app(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "ON_VERCEL": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path / 'v.db').as_posix()}",
        "SECRET_KEY": "a-long-random-production-secret",
    }
    return create_app({**config, **overrides})


def test_vercel_needs_a_database(tmp_path):
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        vercel_app(tmp_path, SQLALCHEMY_DATABASE_URI=None)


def test_vercel_needs_a_real_secret_key(tmp_path):
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        vercel_app(tmp_path, SECRET_KEY="dev-only-not-secret")


def test_vercel_builds_https_urls_behind_its_proxy(tmp_path):
    # Photo URLs use url_for(..., _external=True); behind Vercel's proxy they must be https + the real host.
    from flask import url_for

    app = vercel_app(tmp_path)
    app.add_url_rule("/_url", "url_probe", lambda: url_for("health.health", _external=True))
    response = app.test_client().get(
        "/_url", headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "mogmatch.vercel.app"}
    )
    assert response.get_data(as_text=True) == "https://mogmatch.vercel.app/api/health"
