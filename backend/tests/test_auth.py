from app.models import Profile


def credentials(app, username="jordan-dev", password=None):
    return {"username": username, "password": password or app.config["SEED_PASSWORD"]}


# ---------- logging in and out ----------

def test_login_sets_the_session(app, anon_client):
    assert anon_client.get("/api/auth/session").get_json() == {"user": None}

    response = anon_client.post("/api/auth/login", json=credentials(app))
    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "jordan-dev"
    assert anon_client.get("/api/auth/session").get_json()["user"]["username"] == "jordan-dev"
    assert anon_client.get("/api/profiles/me").get_json()["username"] == "jordan-dev"


def test_username_ignores_case_and_a_leading_at(app, anon_client):
    response = anon_client.post("/api/auth/login", json=credentials(app, "@SamFullStack"))
    assert response.get_json()["user"]["username"] == "samfullstack"


def test_wrong_password_and_unknown_user_get_the_same_401(app, anon_client):
    wrong = anon_client.post("/api/auth/login", json=credentials(app, password="nope"))
    unknown = anon_client.post("/api/auth/login", json=credentials(app, "nobody-here"))
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.get_json() == unknown.get_json()  # can't tell which usernames exist
    assert anon_client.get("/api/auth/session").get_json() == {"user": None}


def test_login_validation(anon_client):
    response = anon_client.post("/api/auth/login", json={"username": " "})
    assert response.status_code == 400
    assert set(response.get_json()["error"]["fields"]) == {"username", "password"}
    assert anon_client.post("/api/auth/login", data="not json").status_code == 400


def test_logout(client):
    assert client.post("/api/auth/logout").get_json() == {"user": None}
    assert client.get("/api/profiles/me").status_code == 401


def test_me_endpoints_need_a_login(anon_client):
    for method, path in [
        ("get", "/api/profiles/me"),
        ("patch", "/api/profiles/me"),
        ("get", "/api/profiles/me/matches"),
        ("post", "/api/swipes"),
        ("delete", "/api/swipes"),
        ("get", "/api/invites/inbox"),
        ("post", "/api/invites"),
    ]:
        response = getattr(anon_client, method)(path, json={})
        assert response.status_code == 401, (method, path)


def test_discover_works_logged_out(anon_client):
    # Public: shows everyone, since there's no "me" to hide.
    assert anon_client.get("/api/profiles").status_code == 200


# ---------- two people, one invite ----------

def test_invite_travels_from_one_user_to_another(app, log_in):
    jordan = log_in(app.test_client(), "jordan-dev")
    sam = log_in(app.test_client(), "samfullstack")
    sam_id = str(Profile.query.filter_by(username="samfullstack").one().id)

    jordan.post("/api/swipes", json={"target_id": sam_id, "action": "like"})
    sent = jordan.post("/api/invites", json={"recipient_id": sam_id, "message": "Build something?"})
    assert sent.status_code == 201

    # Sam's inbox is the same table, read with Sam as the recipient.
    received = sam.get("/api/invites/inbox").get_json()["received"]
    assert [(i["sender"]["username"], i["message"]) for i in received] == [("jordan-dev", "Build something?")]

    # Jordan can't answer their own invite; Sam can.
    invite_id = received[0]["id"]
    assert jordan.patch(f"/api/invites/{invite_id}", json={"status": "accepted"}).status_code == 404
    assert sam.patch(f"/api/invites/{invite_id}", json={"status": "accepted"}).status_code == 200
    assert jordan.get("/api/invites/inbox").get_json()["sent"][0]["status"] == "accepted"


def test_each_user_has_their_own_profile_and_matches(app, log_in):
    jordan = log_in(app.test_client(), "jordan-dev")
    sam = log_in(app.test_client(), "samfullstack")
    maya_id = str(Profile.query.filter_by(username="mayacodes").one().id)

    sam.post("/api/swipes", json={"target_id": maya_id, "action": "like"})
    assert [m["username"] for m in sam.get("/api/profiles/me/matches").get_json()["matches"]] == ["mayacodes"]
    assert jordan.get("/api/profiles/me/matches").get_json()["count"] == 0

    # Discover hides the logged-in user, so Sam sees Jordan and Jordan sees Sam.
    sam_sees = {p["username"] for p in sam.get("/api/profiles").get_json()["profiles"]}
    assert "jordan-dev" in sam_sees and "samfullstack" not in sam_sees
