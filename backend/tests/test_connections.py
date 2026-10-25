"""Connection changes must apply to both participants, including existing sockets."""
import uuid

import pytest

from app.extensions import db, socketio
from app.models import ChatMessage, Invite, Profile, ProjectIdea, StudioTurn, UserBlock
from app.services import idea_service
from app.seed import seed_database


@pytest.fixture
def matched(app, client, log_in):
    invite = next(row for row in client.get("/api/invites/inbox").json["received"]
                  if row["sender"]["username"] == "priya-ml")
    assert client.patch(f"/api/invites/{invite['id']}", json={"status": "accepted"}).status_code == 200
    other = log_in(app.test_client(), "priya-ml")
    sockets = [socketio.test_client(app, flask_test_client=c) for c in (client, other)]
    yield invite, other, sockets
    for ws in sockets:
        if ws.is_connected():
            ws.disconnect()


def send(ws, invite_id, body="A message worth keeping"):
    return ws.emit("chat:send", {"conversation_id": invite_id, "body": body,
                               "client_token": str(uuid.uuid4())}, callback=True)


def test_unmatch_preserves_history_but_requires_fresh_acceptance(app, client, matched):
    invite, other, sockets = matched
    invite_id = invite["id"]
    message = send(sockets[0], invite_id)["message"]
    assert client.post(f"/api/conversations/{invite_id}/unmatch").status_code == 200
    for participant, ws in zip((client, other), sockets):
        thread = participant.get("/api/conversations").json["conversations"][0]
        assert thread["id"] == invite_id and not thread["can_message"] and thread["status"] == "unmatched"
        assert participant.get(f"/api/conversations/{invite_id}/messages").json["messages"] == [message]
        assert send(ws, invite_id)["status"] == 409
        assert participant.post(f"/api/conversations/{invite_id}/ideas", json={}).status_code == 409
        assert any(event["name"] == "connection:updated" for event in ws.get_received())
    assert client.get("/api/profiles/me/matches").json["count"] == 0
    # The other direction can initiate a rematch using the original conversation id.
    rematch = other.post("/api/invites", json={"recipient_id": invite["recipient"]["id"]})
    assert rematch.status_code == 201 and rematch.json["id"] == invite_id
    assert send(sockets[1], invite_id)["status"] == 409
    # The requester cannot approve their own rematch.
    assert other.patch(f"/api/invites/{invite_id}", json={"status": "accepted"}).status_code == 404
    assert client.patch(f"/api/invites/{invite_id}", json={"status": "accepted"}).status_code == 200
    assert "message" in send(sockets[0], invite_id, "Back together")
    assert "message" in send(sockets[1], invite_id, "Accepted together")
    assert client.get(f"/api/conversations/{invite_id}/messages").json["messages"][0] == message
    assert db.session.get(Invite, uuid.UUID(invite_id)).unmatched_at is None


def test_block_hides_both_sides_without_deleting_data(app, client, matched):
    invite, other, sockets = matched
    invite_id = invite["id"]
    send(sockets[0], invite_id)
    assert client.post(f"/api/conversations/{invite_id}/block").status_code == 200
    for participant, ws, target in ((client, sockets[0], invite["sender"]["id"]),
                                    (other, sockets[1], invite["recipient"]["id"])):
        assert participant.get("/api/conversations").json["conversations"] == []
        inbox = participant.get("/api/invites/inbox").json
        assert invite_id not in [row["id"] for row in inbox["sent"] + inbox["received"]]
        assert participant.get(f"/api/conversations/{invite_id}/messages").status_code == 404
        assert participant.get(f"/api/conversations/{invite_id}/ideas").status_code == 404
        assert send(ws, invite_id)["status"] == 404
        assert participant.post("/api/invites", json={"recipient_id": target}).status_code == 404
        assert participant.post("/api/swipes", json={"target_id": target, "action": "like"}).status_code == 404
        assert participant.get(f"/api/profiles/{target}").status_code == 404
        assert target not in [row["id"] for row in participant.get("/api/profiles").json["profiles"]]
        assert any(event["name"] == "connection:updated" for event in ws.get_received())
    db.session.expire_all()
    assert UserBlock.query.count() == 1
    assert ChatMessage.query.filter_by(invite_id=uuid.UUID(invite_id)).count() == 1
    assert db.session.get(Invite, uuid.UUID(invite_id)) is not None
    # Re-running demo seeds cannot restore a blocked connection.
    seed_database()
    assert client.get("/api/conversations").json["conversations"] == []


@pytest.mark.parametrize("action", ["unmatch", "block"])
def test_only_active_match_participants_can_end_a_connection(app, client, log_in, matched, action):
    invite, other, _ = matched
    outsider = log_in(app.test_client(), "samfullstack")
    assert outsider.post(f"/api/conversations/{invite['id']}/{action}").status_code == 404
    assert app.test_client().post(f"/api/conversations/{invite['id']}/{action}").status_code == 401
    pending = next(row for row in client.get("/api/invites/inbox").json["received"] if row["status"] == "pending")
    assert client.post(f"/api/conversations/{pending['id']}/{action}").status_code == 409
    assert client.post(f"/api/conversations/{uuid.uuid4()}/{action}").status_code == 404
    assert client.post(f"/api/conversations/{invite['id']}/unmatch").status_code == 200
    assert client.post(f"/api/conversations/{invite['id']}/{action}").status_code == 409
    assert UserBlock.query.count() == 0


def test_cancel_and_decline_rematch_keep_original_messages(app, client, matched):
    invite, other, sockets = matched
    invite_id = invite["id"]
    send(sockets[0], invite_id)
    assert client.post(f"/api/conversations/{invite_id}/unmatch").status_code == 200
    for direction in (client, other):
        target = invite["sender"]["id"] if direction is client else invite["recipient"]["id"]
        assert direction.post("/api/invites", json={"recipient_id": target}).status_code == 201
        assert direction.delete(f"/api/invites/{invite_id}").status_code == 200
        assert client.get(f"/api/conversations/{invite_id}/messages").json["messages"]
    assert client.post("/api/invites", json={"recipient_id": invite["sender"]["id"]}).status_code == 201
    assert other.patch(f"/api/invites/{invite_id}", json={"status": "declined"}).status_code == 200
    assert client.get(f"/api/conversations/{invite_id}/messages").status_code == 200
    assert send(sockets[0], invite_id)["status"] == 409
    assert other.post("/api/invites", json={"recipient_id": invite["recipient"]["id"]}).status_code == 201


def test_unmatched_studio_is_read_only_and_blocked_studio_is_inaccessible(app, client, matched):
    invite, _, _ = matched
    invite_id = uuid.UUID(invite["id"])
    idea = ProjectIdea(invite_id=invite_id, generated_by=uuid.UUID(invite["recipient"]["id"]),
                       content={"title": "Kept plan"}, model="test")
    db.session.add(idea)
    db.session.flush()
    turn = StudioTurn(idea_id=idea.id, author_id=idea.generated_by, client_token=str(uuid.uuid4()),
                      mode="ask", prompt="Hi", answer="Hello", model="test", change_summary=[])
    db.session.add(turn)
    db.session.commit()
    path = f"/api/conversations/{invite_id}/ideas/{idea.id}/assistant"
    assert client.post(f"/api/conversations/{invite_id}/unmatch").status_code == 200
    assert client.get(path).status_code == 200
    assert client.post(path, json={}).status_code == 409
    assert client.post(f"{path}/{turn.id}/apply").status_code == 409
    db.session.get(Invite, invite_id).status = "accepted"
    db.session.commit()
    assert client.post(f"/api/conversations/{invite_id}/block").status_code == 200
    assert client.get(path).status_code == 404
    assert ProjectIdea.query.count() == 1 and StudioTurn.query.count() == 1


def test_block_during_provider_call_does_not_save_or_broadcast_plan(app, client, matched, monkeypatch):
    invite, _, _ = matched
    app.config["OPENAI_API_KEY"] = "stub"
    def block_during_request(context):
        from app.services.connection_service import end_connection
        me = Profile.query.filter_by(username="jordan-dev").one()
        end_connection(me, uuid.UUID(invite["id"]), block=True)
        return {"title": "Should never be saved"}
    monkeypatch.setattr(idea_service, "request_plan", block_during_request)
    assert client.post(f"/api/conversations/{invite['id']}/ideas", json={}).status_code == 404
    assert ProjectIdea.query.count() == 0
