import uuid

from app.models import Invite, Profile
from app.seed import SEED_INVITES, seed_database


def profile_id(username):
    return str(Profile.query.filter_by(username=username).one().id)


def like(client, username):
    return client.post("/api/swipes", json={"target_id": profile_id(username), "action": "like"})


def invite(client, username, message=None):
    body = {"recipient_id": profile_id(username)}
    if message is not None:
        body["message"] = message
    return client.post("/api/invites", json=body)


def inbox(client):
    return client.get("/api/invites/inbox").get_json()


# ---------- sending ----------

def test_invite_someone_i_liked_shows_up_in_sent(client):
    like(client, "samfullstack")
    response = invite(client, "samfullstack", "  Build a hackathon project?  ")
    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "pending"
    assert body["message"] == "Build a hackathon project?"  # trimmed
    assert body["recipient"]["username"] == "samfullstack"

    sent = inbox(client)["sent"]
    assert [i["recipient"]["username"] for i in sent] == ["samfullstack"]


def test_empty_message_is_stored_as_none(client):
    like(client, "samfullstack")
    assert invite(client, "samfullstack", "   ").get_json()["message"] is None


def test_cant_invite_someone_i_havent_liked(client):
    response = invite(client, "samfullstack")
    assert response.status_code == 400
    assert "recipient_id" in response.get_json()["error"]["fields"]


def test_cant_invite_someone_i_passed_on(client):
    client.post("/api/swipes", json={"target_id": profile_id("diego-rs"), "action": "pass"})
    assert invite(client, "diego-rs").status_code == 400


def test_inviting_twice_is_a_conflict(client):
    like(client, "samfullstack")
    invite(client, "samfullstack")
    assert invite(client, "samfullstack").status_code == 409
    assert len(inbox(client)["sent"]) == 1


def test_cant_invite_someone_who_already_invited_me(client):
    like(client, "priya-ml")  # priya's invite to me is seeded
    response = invite(client, "priya-ml")
    assert response.status_code == 409
    assert "inbox" in response.get_json()["error"]["message"]


def test_invite_validation(client):
    me = client.get("/api/profiles/me").get_json()["id"]
    assert client.post("/api/invites", json={"recipient_id": me}).status_code == 400
    assert client.post("/api/invites", json={"recipient_id": "nope"}).status_code == 400
    assert client.post("/api/invites", json={"recipient_id": str(uuid.uuid4())}).status_code == 404
    assert client.post("/api/invites", data="not json").status_code == 400

    like(client, "samfullstack")
    too_long = invite(client, "samfullstack", "x" * 281)
    assert too_long.status_code == 400
    assert "message" in too_long.get_json()["error"]["fields"]
    extra = client.post("/api/invites", json={"recipient_id": profile_id("samfullstack"), "sender_id": me})
    assert extra.get_json()["error"]["fields"]["sender_id"] == "Unknown field."


# ---------- inbox + responding ----------

def test_seeded_invites_arrive_in_my_inbox(client):
    body = inbox(client)
    senders = {i["sender"]["username"] for i in body["received"]}
    assert senders == {username for username, _ in SEED_INVITES}
    assert body["pending_count"] == len(SEED_INVITES)
    assert body["sent"] == []


def test_accept_and_decline(client):
    first, second = inbox(client)["received"][:2]
    accepted = client.patch(f"/api/invites/{first['id']}", json={"status": "accepted"})
    assert accepted.status_code == 200
    assert accepted.get_json()["status"] == "accepted"
    assert client.patch(f"/api/invites/{second['id']}", json={"status": "declined"}).status_code == 200
    assert inbox(client)["pending_count"] == len(SEED_INVITES) - 2

    # Answering again is a conflict, not a silent change of mind.
    assert client.patch(f"/api/invites/{first['id']}", json={"status": "declined"}).status_code == 409


def test_respond_validation(client):
    invite_id = inbox(client)["received"][0]["id"]
    assert client.patch(f"/api/invites/{invite_id}", json={"status": "maybe"}).status_code == 400
    assert client.patch(f"/api/invites/{uuid.uuid4()}", json={"status": "accepted"}).status_code == 404


def test_cant_answer_my_own_invite(client):
    like(client, "samfullstack")
    invite_id = invite(client, "samfullstack").get_json()["id"]
    # Only the recipient can answer; to the sender it looks like it doesn't exist.
    assert client.patch(f"/api/invites/{invite_id}", json={"status": "accepted"}).status_code == 404


# ---------- cancelling ----------

def test_cancel_a_pending_invite(client):
    like(client, "samfullstack")
    invite_id = invite(client, "samfullstack").get_json()["id"]
    assert client.delete(f"/api/invites/{invite_id}").status_code == 200
    assert inbox(client)["sent"] == []
    assert invite(client, "samfullstack").status_code == 201  # can invite again after cancelling


def test_cant_cancel_someone_elses_invite(client):
    received_id = inbox(client)["received"][0]["id"]
    assert client.delete(f"/api/invites/{received_id}").status_code == 404
    assert client.delete(f"/api/invites/{uuid.uuid4()}").status_code == 404


# ---------- seed ----------

def test_seed_keeps_invite_answers_and_does_not_duplicate(client):
    invite_id = inbox(client)["received"][0]["id"]
    client.patch(f"/api/invites/{invite_id}", json={"status": "accepted"})

    seed_database()
    assert Invite.query.count() == len(SEED_INVITES)
    assert inbox(client)["pending_count"] == len(SEED_INVITES) - 1

    seed_database(reset=True)  # reset puts every seeded invite back to pending
    assert inbox(client)["pending_count"] == len(SEED_INVITES)
