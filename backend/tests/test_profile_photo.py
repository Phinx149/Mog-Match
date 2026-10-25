import json
import uuid
from io import BytesIO
from urllib.parse import urlsplit

from PIL import Image

from app.models import User


def photo_file():
    output = BytesIO()
    Image.new("RGB", (12, 12), "purple").save(output, format="PNG")
    return output.getvalue()


def test_photo_saved_in_user_and_served_after_reload(client, app):
    raw = photo_file()
    category = client.get("/api/profiles/filter-options").get_json()["looking_for"][0]
    response = client.patch("/api/profiles/me", data={
        "profile": json.dumps({"full_name": "Photo User", "looking_for": [category]}),
        "photo": (BytesIO(raw), "avatar.png"),
    })
    assert response.status_code == 200
    profile = client.get("/api/profiles/me").get_json()
    assert profile["looking_for"] == [category]
    path = urlsplit(profile["avatar_url"]).path
    image = client.get(path)
    assert image.status_code == 200
    assert image.data == raw
    assert image.mimetype == "image/png"
    with app.app_context():
        user = User.query.filter_by(id=uuid.UUID(profile["user_id"])).one()
        assert user.photo_data == raw
        assert user.photo_mimetype == "image/png"


def test_invalid_photo_and_all_fields_reported_without_saving(client):
    original = client.get("/api/profiles/me").get_json()
    taken = client.get("/api/profiles").get_json()["profiles"][0]["username"]
    response = client.patch("/api/profiles/me", data={
        "profile": json.dumps({"username": taken, "full_name": "", "skills": ["fake-tech-xyz"],
                               "links": [{"label": "", "url": "bad"}],
                               "projects": [{"title": "", "technologies": ["fake-tech-xyz"]}]}),
        "photo": (BytesIO(b"not an image"), "avatar.png"),
    })
    assert response.status_code == 409
    assert set(response.get_json()["error"]["fields"]) == {
        "username", "full_name", "skills", "links[0].label", "links[0].url",
        "projects[0].title", "projects[0].description", "projects[0].technologies", "photo",
    }
    assert client.get("/api/profiles/me").get_json() == original


def test_photo_not_saved_when_profile_invalid(client):
    response = client.patch("/api/profiles/me", data={
        "profile": json.dumps({"full_name": ""}),
        "photo": (BytesIO(photo_file()), "avatar.png"),
    })
    assert response.status_code == 400
    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}/photo").status_code == 404


def test_oversize_photo_rejected(client):
    response = client.patch("/api/profiles/me", data={
        "profile": "{}", "photo": (BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "large.png"),
    })
    assert response.status_code == 400
    assert "photo" in response.get_json()["error"]["fields"]
