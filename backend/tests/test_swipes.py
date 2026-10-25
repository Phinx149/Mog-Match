import uuid

from app.models import Profile


def profile_id(client, username):
    # Straight from the DB: Discover hides people you've already swiped on.
    return str(Profile.query.filter_by(username=username).one().id)


def swipe(client, username, action="like"):
    return client.post("/api/swipes", json={"target_id": profile_id(client, username), "action": action})


def test_no_matches_until_i_like_someone(client):
    assert client.get("/api/profiles/me/matches").get_json() == {"matches": [], "count": 0}


def test_like_returns_a_match_score_and_shows_up_in_matches(client):
    response = swipe(client, "samfullstack")
    assert response.status_code == 201
    body = response.get_json()
    assert body["action"] == "like"
    assert 0 <= body["match"]["score"] <= 100

    matches = client.get("/api/profiles/me/matches").get_json()["matches"]
    assert [m["username"] for m in matches] == ["samfullstack"]
    assert matches[0]["match"] == body["match"]


def test_pass_is_not_a_match(client):
    body = swipe(client, "diego-rs", "pass").get_json()
    assert body["match"] is None
    assert client.get("/api/profiles/me/matches").get_json()["count"] == 0


def test_matches_are_ranked_most_similar_first(client):
    for username in ["lena-gamedev", "samfullstack", "kenji-mobile", "mayacodes"]:
        swipe(client, username)
    matches = client.get("/api/profiles/me/matches").get_json()["matches"]
    scores = [m["match"]["score"] for m in matches]
    assert len(matches) == 4
    assert scores == sorted(scores, reverse=True)
    assert matches[0]["username"] == "samfullstack"  # shares Full-stack, React and Startups with Jordan


def test_swiping_again_overwrites_instead_of_duplicating(client):
    swipe(client, "mayacodes")
    swipe(client, "mayacodes")
    assert client.get("/api/profiles/me/matches").get_json()["count"] == 1
    swipe(client, "mayacodes", "pass")
    assert client.get("/api/profiles/me/matches").get_json()["count"] == 0


def test_discover_hides_swiped_profiles_until_cleared(client):
    total = client.get("/api/profiles").get_json()["count"]
    swipe(client, "mayacodes")
    swipe(client, "diego-rs", "pass")
    usernames = {p["username"] for p in client.get("/api/profiles").get_json()["profiles"]}
    assert len(usernames) == total - 2
    assert not {"mayacodes", "diego-rs"} & usernames

    assert client.delete("/api/swipes").get_json() == {"removed": 2}
    assert client.get("/api/profiles").get_json()["count"] == total
    assert client.get("/api/profiles/me/matches").get_json()["count"] == 0


def test_swipe_validation(client):
    me = client.get("/api/profiles/me").get_json()
    cases = [
        ({"target_id": "nope", "action": "like"}, "target_id"),
        ({"target_id": me["id"], "action": "like"}, "target_id"),  # can't like yourself
        ({"target_id": profile_id(client, "mayacodes"), "action": "superlike"}, "action"),
        ({"target_id": profile_id(client, "mayacodes"), "action": "like", "swiper_id": me["id"]}, "swiper_id"),
    ]
    for body, field in cases:
        response = client.post("/api/swipes", json=body)
        assert response.status_code == 400, body
        assert field in response.get_json()["error"]["fields"]
    assert client.post("/api/swipes", data="x", content_type="application/json").status_code == 400


def test_swipe_on_unknown_profile_is_404(client):
    response = client.post("/api/swipes", json={"target_id": str(uuid.uuid4()), "action": "like"})
    assert response.status_code == 404


def test_seed_reset_clears_swipes(app, client, log_in):
    from app.seed import seed_database

    swipe(client, "mayacodes")
    seed_database(reset=True)
    log_in(client)  # reset recreates users, which logs everyone out
    assert client.get("/api/profiles/me/matches").get_json()["count"] == 0


def test_unlike_removes_the_match_and_brings_them_back_to_discover(client):
    maya = profile_id(client, "mayacodes")
    swipe(client, "mayacodes")
    swipe(client, "samfullstack")

    response = client.delete(f"/api/swipes/{maya}")
    assert response.status_code == 200
    assert response.get_json() == {"removed": True}

    matches = client.get("/api/profiles/me/matches").get_json()["matches"]
    assert [m["username"] for m in matches] == ["samfullstack"]  # the other like is untouched
    discover = {p["username"] for p in client.get("/api/profiles").get_json()["profiles"]}
    assert "mayacodes" in discover and "samfullstack" not in discover


def test_unlike_someone_never_liked_is_404(client):
    assert client.delete(f"/api/swipes/{profile_id(client, 'mayacodes')}").status_code == 404
    assert client.delete(f"/api/swipes/{uuid.uuid4()}").status_code == 404
    assert client.delete("/api/swipes/not-a-uuid").status_code == 404


# ---------- GET /api/swipes/<id>: the profile page's Like button ----------

def test_get_swipe_reports_like_pass_or_nothing(client):
    maya, diego = profile_id(client, "mayacodes"), profile_id(client, "diego-rs")
    assert client.get(f"/api/swipes/{maya}").get_json() == {"target_id": maya, "action": None}

    swipe(client, "mayacodes", "like")
    swipe(client, "diego-rs", "pass")
    assert client.get(f"/api/swipes/{maya}").get_json()["action"] == "like"
    assert client.get(f"/api/swipes/{diego}").get_json()["action"] == "pass"

    client.delete(f"/api/swipes/{maya}")  # unlike from the profile page
    assert client.get(f"/api/swipes/{maya}").get_json()["action"] is None


def test_get_swipe_unknown_profile_and_logged_out(client, anon_client):
    assert client.get(f"/api/swipes/{uuid.uuid4()}").status_code == 404
    maya = profile_id(client, "mayacodes")
    assert anon_client.get(f"/api/swipes/{maya}").status_code == 401


def test_get_swipe_only_shows_my_own_likes(app, log_in):
    jordan = log_in(app.test_client(), "jordan-dev")
    sam = log_in(app.test_client(), "samfullstack")
    maya = str(Profile.query.filter_by(username="mayacodes").one().id)
    jordan.post("/api/swipes", json={"target_id": maya, "action": "like"})
    assert sam.get(f"/api/swipes/{maya}").get_json()["action"] is None  # Sam hasn't liked Maya
