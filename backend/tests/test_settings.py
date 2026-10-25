import pytest
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import Profile


def test_display_name_persists_in_session_and_public_profile(client):
    before = client.get("/api/profiles/me").get_json()
    response = client.patch("/api/profiles/me", json={"full_name": "  Hackathon Builder  "})
    assert response.status_code == 200
    db.session.remove()
    assert client.get("/api/auth/session").get_json()["user"]["full_name"] == "Hackathon Builder"
    public = client.get(f"/api/profiles/{before['id']}").get_json()
    assert public["full_name"] == "Hackathon Builder"
    assert public["username"] == before["username"]


def test_password_change_persists_and_replaces_old_login(app, client, anon_client):
    response = client.patch("/api/auth/password", json={
        "current_password": app.config["SEED_PASSWORD"], "new_password": "new-hackathon-password",
    })
    assert response.status_code == 200
    db.session.remove()
    profile = Profile.query.filter_by(username="jordan-dev").one()
    assert profile.user.password_hash != "new-hackathon-password"
    assert check_password_hash(profile.user.password_hash, "new-hackathon-password")
    assert client.get("/api/auth/session").get_json()["user"] is not None
    assert anon_client.post("/api/auth/login", json={
        "username": "jordan-dev", "password": app.config["SEED_PASSWORD"],
    }).status_code == 401
    assert anon_client.post("/api/auth/login", json={
        "username": "jordan-dev", "password": "new-hackathon-password",
    }).status_code == 200


@pytest.mark.parametrize("new_password", [None, 123, "short", " " * 8, "x" * 129])
def test_invalid_new_password_does_not_change_credentials(app, client, new_password):
    response = client.patch("/api/auth/password", json={
        "current_password": app.config["SEED_PASSWORD"], "new_password": new_password,
    })
    assert response.status_code == 400
    assert "new_password" in response.get_json()["error"]["fields"]
    assert client.post("/api/auth/login", json={
        "username": "jordan-dev", "password": app.config["SEED_PASSWORD"],
    }).status_code == 200


def test_wrong_current_password_keeps_session_and_credentials(app, client):
    response = client.patch("/api/auth/password", json={
        "current_password": "incorrect", "new_password": "new-hackathon-password",
    })
    assert response.status_code == 400
    assert "current_password" in response.get_json()["error"]["fields"]
    assert client.get("/api/auth/session").get_json()["user"] is not None
    assert client.post("/api/auth/login", json={
        "username": "jordan-dev", "password": app.config["SEED_PASSWORD"],
    }).status_code == 200


def test_password_change_requires_login(anon_client):
    assert anon_client.patch("/api/auth/password", json={
        "current_password": "anything", "new_password": "another-password",
    }).status_code == 401


def test_password_change_rejects_missing_body_and_same_password(app, client):
    assert client.patch("/api/auth/password").status_code == 400
    password = app.config["SEED_PASSWORD"]
    assert client.patch("/api/auth/password", json={
        "current_password": password, "new_password": password,
    }).status_code == 400
