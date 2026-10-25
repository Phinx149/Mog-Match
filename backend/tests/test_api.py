import uuid
import json

import pytest

from app.seed import SEED_PROFILES, seed_database


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_list_profiles_excludes_demo_user(client):
    me = client.get("/api/profiles/me").get_json()
    body = client.get("/api/profiles").get_json()

    assert body["count"] == len(SEED_PROFILES)
    assert me["id"] not in {p["id"] for p in body["profiles"]}


def test_get_profile_by_id(client):
    first = client.get("/api/profiles").get_json()["profiles"][0]
    response = client.get(f"/api/profiles/{first['id']}")

    assert response.status_code == 200
    profile = response.get_json()
    assert profile["username"] == first["username"]
    assert isinstance(profile["projects"], list) and profile["projects"]
    assert isinstance(profile["links"], list) and profile["links"]


def test_nonexistent_profile_returns_404(client):
    response = client.get(f"/api/profiles/{uuid.uuid4()}")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_malformed_profile_id_returns_404(client):
    assert client.get("/api/profiles/not-a-uuid").status_code == 404


def test_filter_by_skills_is_case_insensitive_and_requires_all(client):
    rust = client.get("/api/profiles?skills=rust").get_json()["profiles"]
    assert rust and all("rust" in [s.lower() for s in p["skills"]] for p in rust)

    both = client.get("/api/profiles?skills=Rust,Frontend").get_json()["profiles"]
    assert [p["username"] for p in both] == ["noah-learns"]


def test_filter_by_looking_for_matches_any_selected_option(client):
    mentors = client.get("/api/profiles?looking_for=mentor").get_json()["profiles"]
    assert sorted(p["username"] for p in mentors) == ["noah-learns", "samfullstack"]

    either = client.get("/api/profiles?looking_for=Mentor,Mentee").get_json()["profiles"]
    assert len(either) == 5

    combined = client.get("/api/profiles?looking_for=Mentor&skills=Rust").get_json()["profiles"]
    assert [p["username"] for p in combined] == ["noah-learns"]


def test_filter_options_lists_every_allowed_skill_and_looking_for(client):
    from app.services.profile_service import LOOKING_FOR_OPTIONS
    from app.services.tech_catalog import ALL_TECHNOLOGIES

    options = client.get("/api/profiles/filter-options").get_json()

    assert set(options["skills"]) == ALL_TECHNOLOGIES
    assert options["skills"] == sorted(options["skills"], key=str.lower)
    assert options["looking_for"] == list(LOOKING_FOR_OPTIONS)
    assert {"Open source", "Cofounder"} <= set(options["looking_for"])


def test_new_looking_for_options_have_matches(client):
    for option, expected in [("Open source", 2), ("Cofounder", 2)]:
        found = client.get("/api/profiles", query_string={"looking_for": option}).get_json()
        assert found["count"] == expected, option


def test_update_looking_for_normalizes_to_allowed_options(client):
    response = client.patch("/api/profiles/me", json={"looking_for": ["mentor", " COFOUNDER ", "Mentor"]})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["looking_for"] == ["Mentor", "Cofounder"]  # canonical spelling, de-duplicated

    cleared = client.patch("/api/profiles/me", json={"looking_for": []})
    assert cleared.status_code == 200
    assert cleared.get_json()["looking_for"] == []


def test_update_rejects_looking_for_outside_the_list(client):
    response = client.patch("/api/profiles/me", json={"looking_for": ["Mentor", "Pizza buddy"]})

    assert response.status_code == 400
    message = response.get_json()["error"]["fields"]["looking_for"]
    assert "Pizza buddy" in message and "Hackathon team" in message
    assert client.get("/api/profiles/me").get_json()["looking_for"] == ["Hackathon team", "Side project"]  # unchanged


def test_search_and_location_filters(client):
    assert [p["username"] for p in client.get("/api/profiles?q=unity").get_json()["profiles"]] == [
        "lena-gamedev"
    ]
    tokyo = client.get("/api/profiles?location=tokyo").get_json()["profiles"]
    assert [p["username"] for p in tokyo] == ["kenji-mobile"]


def test_update_my_profile_persists(client):
    payload = {
        "full_name": "Jordan A.",
        "skills": ["Go", "go", "  Svelte  "],
        "links": [{"label": "GitHub", "url": "https://github.com/someone"}],
        "projects": [{"title": "New thing", "description": "A Go project.", "technologies": ["Go"]}],
    }
    response = client.patch("/api/profiles/me", json=payload)
    assert response.status_code == 200, response.get_json()

    me = client.get("/api/profiles/me").get_json()
    assert me["full_name"] == "Jordan A."
    assert me["skills"] == ["Go", "Svelte"]  # trimmed and de-duplicated
    assert [link["url"] for link in me["links"]] == ["https://github.com/someone"]
    assert [project["title"] for project in me["projects"]] == ["New thing"]
    assert me["location"] == "Austin, TX"  # untouched fields are kept


def test_update_rejects_invalid_data(client):
    response = client.patch(
        "/api/profiles/me",
        json={
            "full_name": "",
            "skills": "Python",
            "links": [{"label": "Bad", "url": "javascript:alert(1)"}],
            "id": "hacked",
        },
    )
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert {"full_name", "skills", "links[0].url", "id"} <= set(fields)


@pytest.mark.parametrize("field", ["bio", "favorite_ide"])
@pytest.mark.parametrize("value", [None, "", " \n\t "])
def test_required_profile_text_cannot_be_cleared(client, field, value):
    before = client.get("/api/profiles/me").get_json()
    response = client.patch("/api/profiles/me", json={field: value, "full_name": "Must not save"})
    assert response.status_code == 400
    assert field in response.get_json()["error"]["fields"]
    after = client.get("/api/profiles/me").get_json()
    assert after[field] == before[field]
    assert after["full_name"] == before["full_name"]


@pytest.mark.parametrize("agents", [None, [], ["", " \t "]])
def test_at_least_one_coding_agent_is_required(client, agents):
    response = client.patch("/api/profiles/me", json={"favorite_ai_agents": agents})
    assert response.status_code == 400
    assert "favorite_ai_agents" in response.get_json()["error"]["fields"]


@pytest.mark.parametrize("value", [None, "", " \n\t "])
def test_location_can_be_cleared(client, value):
    response = client.patch("/api/profiles/me", json={"location": value})
    assert response.status_code == 200
    assert response.get_json()["location"] is None
    assert client.get("/api/profiles/me").get_json()["location"] is None


@pytest.mark.parametrize("project", [
    {"title": "App"},
    {"title": "App", "description": " \t ", "technologies": ["Go"]},
    {"title": "App", "description": "An app", "technologies": [" "]},
    {"title": "App", "description": None, "technologies": None},
])
def test_added_projects_require_description_and_technologies(client, project):
    before = client.get("/api/profiles/me").get_json()["projects"]
    response = client.patch("/api/profiles/me", json={"projects": [project]})
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert any(key in fields for key in ["projects[0].description", "projects[0].technologies"])
    assert client.get("/api/profiles/me").get_json()["projects"] == before


def test_projects_are_optional_and_required_values_are_cleaned(client):
    response = client.patch("/api/profiles/me", json={
        "location": "  Austin  ", "bio": "  I build apps.  ", "favorite_ide": "  VS Code  ",
        "favorite_ai_agents": ["  Codex  ", "codex", ""], "projects": [],
    })
    assert response.status_code == 200
    saved = response.get_json()
    assert saved["location"] == "Austin"
    assert saved["bio"] == "I build apps."
    assert saved["favorite_ide"] == "VS Code"
    assert saved["favorite_ai_agents"] == ["Codex"]
    assert saved["projects"] == []


def test_required_fields_are_validated_for_multipart_saves(client):
    response = client.patch("/api/profiles/me", data={"profile": json.dumps({
        "location": " ", "bio": "", "favorite_ide": None, "favorite_ai_agents": [],
        "projects": [{"title": "App"}],
    })}, content_type="multipart/form-data")
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert {"bio", "favorite_ide", "favorite_ai_agents", "projects[0].description",
            "projects[0].technologies"} <= set(fields)
    assert "location" not in fields


def test_update_rejects_non_object_body(client):
    response = client.patch("/api/profiles/me", data="nope", content_type="application/json")
    assert response.status_code == 400


def test_update_rejects_taken_username(client):
    response = client.patch("/api/profiles/me", json={"username": "MayaCodes"})
    assert response.status_code == 409
    assert "username" in response.get_json()["error"]["fields"]


def test_seed_is_idempotent_and_reset_restores(app, client, log_in):
    client.patch("/api/profiles/me", json={"full_name": "Edited"})

    counts = seed_database()
    assert counts["created"] == 0
    assert client.get("/api/profiles/me").get_json()["full_name"] == "Edited"
    assert client.get("/api/profiles").get_json()["count"] == len(SEED_PROFILES)

    seed_database(reset=True)
    log_in(client)  # reset recreates users, which logs everyone out
    assert client.get("/api/profiles/me").get_json()["full_name"] == "Jordan Avery"



def test_every_field_at_its_max_length_saves(client):
    # Postgres rejects strings longer than the column (SQLite doesn't), so validation limits must
    # never exceed the column sizes. Run with TEST_DATABASE_URL=postgresql://... to check for real.
    from app.services.profile_service import STRING_FIELDS

    update = {
        field: ("https://example.com/" + "a" * (limit - 20) if field == "avatar_url" else "a" * limit)
        for field, (limit, _) in STRING_FIELDS.items()
        if field not in ("experience_level", "username")
    }
    update["username"] = "u" * STRING_FIELDS["username"][0]
    update["links"] = [{"label": "L" * 40, "url": "https://example.com/" + "b" * 480}]
    update["projects"] = [{
        "title": "T" * 120, "description": "D" * 2000,
        "project_url": "https://example.com/" + "c" * 480, "technologies": ["React"],
    }]
    response = client.patch("/api/profiles/me", json=update)
    assert response.status_code == 200, response.get_json()


def test_invite_message_at_max_length_saves(client):
    from app.models import Profile
    from app.services.invite_service import MAX_MESSAGE_LENGTH

    sam = str(Profile.query.filter_by(username="samfullstack").one().id)
    client.post("/api/swipes", json={"target_id": sam, "action": "like"})
    response = client.post("/api/invites", json={"recipient_id": sam, "message": "m" * MAX_MESSAGE_LENGTH})
    assert response.status_code == 201
