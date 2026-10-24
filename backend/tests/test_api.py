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
