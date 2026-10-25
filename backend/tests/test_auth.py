from app.models import Profile, User


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


# ---------- signing up ----------

def new_account(**overrides):
    return {"full_name": "Riley Rookie", "username": "riley-rookie", "password": "correct horse", **overrides}


def test_sign_up_creates_an_account_and_logs_it_in(anon_client):
    response = anon_client.post("/api/auth/signup", json=new_account())
    assert response.status_code == 201
    user = response.get_json()["user"]
    assert (user["full_name"], user["username"]) == ("Riley Rookie", "riley-rookie")
    assert "password" not in str(response.get_json())

    # The session cookie was set, so "me" is the new user straight away...
    assert anon_client.get("/api/auth/session").get_json()["user"]["username"] == "riley-rookie"
    me = anon_client.get("/api/profiles/me").get_json()
    assert me["bio"] == "" and me["skills"] == []  # an empty profile, to be filled in on the edit page
    # ...and the profile can be edited like any other.
    saved = anon_client.patch("/api/profiles/me", json={"bio": "Hi!", "favorite_ide": "Neovim"})
    assert saved.status_code == 200 and saved.get_json()["bio"] == "Hi!"


def test_sign_up_stores_a_hash_and_the_password_works_for_login(app, anon_client):
    anon_client.post("/api/auth/signup", json=new_account())
    stored = Profile.query.filter_by(username="riley-rookie").one().user.password_hash
    assert stored and "correct horse" not in stored

    anon_client.post("/api/auth/logout")
    other_browser = app.test_client()
    wrong = other_browser.post("/api/auth/login", json={"username": "riley-rookie", "password": "wrong password"})
    assert wrong.status_code == 401
    right = other_browser.post("/api/auth/login", json={"username": "Riley-Rookie", "password": "correct horse"})
    assert right.status_code == 200


def test_sign_up_rejects_a_taken_username_in_any_case(anon_client):
    users_before = User.query.count()
    for username in ("jordan-dev", "JORDAN-DEV"):
        response = anon_client.post("/api/auth/signup", json=new_account(username=username))
        assert response.status_code == 409
        assert response.get_json()["error"]["fields"] == {"username": "That username is already taken."}
    assert User.query.count() == users_before
    assert anon_client.get("/api/auth/session").get_json() == {"user": None}  # a failed sign-up logs nobody in


def test_sign_up_validation(anon_client):
    users_before = User.query.count()
    empty = anon_client.post("/api/auth/signup", json={})
    assert empty.status_code == 400
    assert set(empty.get_json()["error"]["fields"]) == {"full_name", "username", "password"}

    bad = anon_client.post(
        "/api/auth/signup",
        json=new_account(username="no spaces!", password="short", full_name="  ", is_admin=True),
    )
    assert bad.status_code == 400
    assert set(bad.get_json()["error"]["fields"]) == {"full_name", "username", "password", "is_admin"}

    too_long = anon_client.post("/api/auth/signup", json=new_account(password="x" * 129))
    assert too_long.status_code == 400 and "password" in too_long.get_json()["error"]["fields"]
    not_strings = anon_client.post("/api/auth/signup", json=new_account(username=7, password=12345678))
    assert set(not_strings.get_json()["error"]["fields"]) == {"username", "password"}
    assert anon_client.post("/api/auth/signup", data="not json").status_code == 400
    assert User.query.count() == users_before


def test_sign_up_accepts_values_at_the_length_limits(anon_client):
    # The same limits as the columns (Postgres rejects longer strings), plus the longest allowed password.
    response = anon_client.post(
        "/api/auth/signup", json=new_account(full_name="n" * 120, username="u" * 40, password="p" * 128)
    )
    assert response.status_code == 201


def test_sign_up_while_logged_in_switches_to_the_new_account(client):
    assert client.get("/api/auth/session").get_json()["user"]["username"] == "jordan-dev"
    assert client.post("/api/auth/signup", json=new_account()).status_code == 201
    assert client.get("/api/auth/session").get_json()["user"]["username"] == "riley-rookie"


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


# ---------- quick-login test users ----------

def test_seed_test_users_can_log_in_and_already_like_each_other(app, anon_client):
    from app.seed import TEST_USERS, seed_test_users, test_accounts

    assert seed_test_users() == len(test_accounts())
    assert seed_test_users() == 0  # idempotent
    first, second = TEST_USERS
    login = {"username": first["username"], "password": first["password"]}
    assert anon_client.post("/api/auth/login", json=login).status_code == 200
    matches = anon_client.get("/api/profiles/me/matches").get_json()["matches"]
    assert [m["username"] for m in matches] == [second["username"]]


def test_seed_test_users_reset_clears_their_invites(app):
    from app.models import Invite
    from app.seed import TEST_USERS, seed_test_users, test_accounts

    seed_test_users()
    first, second = TEST_USERS
    client = app.test_client()
    client.post("/api/auth/login", json={"username": first["username"], "password": first["password"]})
    other_id = str(Profile.query.filter_by(username=second["username"]).one().id)
    assert client.post("/api/invites", json={"recipient_id": other_id}).status_code == 201

    assert seed_test_users(reset=True) == len(test_accounts())
    sender = Profile.query.filter_by(username=first["username"]).one()
    assert Invite.query.filter_by(sender_id=sender.id).count() == 0
