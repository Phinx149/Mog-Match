import uuid

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
        "projects": [{"title": "New thing", "description": "", "technologies": ["Go"]}],
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


def test_update_rejects_non_object_body(client):
    response = client.patch("/api/profiles/me", data="nope", content_type="application/json")
    assert response.status_code == 400


def test_update_rejects_taken_username(client):
    response = client.patch("/api/profiles/me", json={"username": "MayaCodes"})
    assert response.status_code == 409
    assert "username" in response.get_json()["error"]["fields"]


def test_seed_is_idempotent_and_reset_restores(app, client):
    client.patch("/api/profiles/me", json={"full_name": "Edited"})

    counts = seed_database()
    assert counts["created"] == 0
    assert client.get("/api/profiles/me").get_json()["full_name"] == "Edited"
    assert client.get("/api/profiles").get_json()["count"] == len(SEED_PROFILES)

    seed_database(reset=True)
    assert client.get("/api/profiles/me").get_json()["full_name"] == "Jordan Avery"

