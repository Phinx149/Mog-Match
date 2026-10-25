import uuid

import pytest

from app.extensions import db, socketio
from app.models import ChatMessage, Invite, Profile, ProjectIdea
from app.services import idea_service


@pytest.fixture
def thread(client):
    invite = client.get("/api/invites/inbox").json["received"][0]
    assert client.patch(f"/api/invites/{invite['id']}", json={"status": "accepted"}).status_code == 200
    return invite


def payload(thread, body="Let's build something.", token=None):
    return {"conversation_id": thread["id"], "body": body, "client_token": token or str(uuid.uuid4())}


def test_socket_rejects_anonymous_and_http_requires_login(app, anon_client):
    ws = socketio.test_client(app, flask_test_client=anon_client)
    assert not ws.is_connected()
    assert anon_client.get("/api/conversations").status_code == 401


def test_acceptance_creates_one_shared_thread_and_only_members_can_access(app, client, log_in, thread):
    other = log_in(app.test_client(), thread["sender"]["username"])
    outsider = log_in(app.test_client(), "samfullstack")
    assert client.get("/api/conversations").json["conversations"][0]["id"] == thread["id"]
    assert other.get("/api/conversations").json["conversations"][0]["id"] == thread["id"]
    for suffix in ("messages", "ideas"):
        assert outsider.get(f"/api/conversations/{thread['id']}/{suffix}").status_code == 404
    assert outsider.post(f"/api/conversations/{thread['id']}/ideas", json={}).status_code == 404
    assert outsider.post(f"/api/conversations/{thread['id']}/read", json={"message_id": 1}).status_code == 404


def test_socket_delivery_is_private_persistent_and_retry_safe(app, client, log_in, thread):
    other = log_in(app.test_client(), thread["sender"]["username"])
    outsider = log_in(app.test_client(), "samfullstack")
    sender = socketio.test_client(app, flask_test_client=client)
    receiver = socketio.test_client(app, flask_test_client=other)
    third = socketio.test_client(app, flask_test_client=outsider)
    data = payload(thread, "  React and Python, weekend MVP?  ")
    ack = sender.emit("chat:send", data, callback=True)
    assert ack["message"]["body"] == data["body"].strip()
    assert receiver.get_received()[0]["args"][0]["id"] == ack["message"]["id"]
    assert third.get_received() == []
    assert sender.emit("chat:send", data, callback=True) == ack
    assert receiver.get_received() == []
    assert ChatMessage.query.count() == 1
    sender.disconnect()
    sender = socketio.test_client(app, flask_test_client=client)
    reply = receiver.emit("chat:send", payload(thread, "Yes! Keep it free to host."), callback=True)
    assert reply["message"]["sender_id"] == thread["sender"]["id"]
    assert sender.get_received()[0]["name"] == "chat:message"
    history = client.get(f"/api/conversations/{thread['id']}/messages").json
    assert len(history["messages"]) == 2
    assert history["messages"][0]["id"] < history["messages"][1]["id"]
    assert other.get("/api/conversations").json["conversations"][0]["unread_count"] == 1
    read = other.post(f"/api/conversations/{thread['id']}/read", json={"message_id": ack["message"]["id"]})
    assert read.status_code == 200
    assert other.get("/api/conversations").json["conversations"][0]["unread_count"] == 0
    sender.disconnect(); receiver.disconnect(); third.disconnect()


def test_socket_refuses_pending_declined_and_unrelated_threads(app, client, log_in):
    invites = client.get("/api/invites/inbox").json["received"]
    ws = socketio.test_client(app, flask_test_client=client)
    assert ws.emit("chat:send", payload(invites[0]), callback=True)["status"] == 404
    client.patch(f"/api/invites/{invites[0]['id']}", json={"status": "declined"})
    assert ws.emit("chat:send", payload(invites[0]), callback=True)["status"] == 404
    client.patch(f"/api/invites/{invites[1]['id']}", json={"status": "accepted"})
    outsider = log_in(app.test_client(), "samfullstack")
    third = socketio.test_client(app, flask_test_client=outsider)
    assert third.emit("chat:send", payload(invites[1]), callback=True)["status"] == 404
    assert ChatMessage.query.count() == 0
    ws.disconnect(); third.disconnect()


@pytest.mark.parametrize("patch", [{"body": " "}, {"body": "x" * 2001}, {"body": None},
                                    {"client_token": "bad"}, {"sender_id": "spoofed"}])
def test_message_validation(app, client, thread, patch):
    ws = socketio.test_client(app, flask_test_client=client)
    ack = ws.emit("chat:send", {**payload(thread), **patch}, callback=True)
    assert ack["status"] == 400
    assert ChatMessage.query.count() == 0
    ws.disconnect()


def test_logout_revokes_existing_socket(app, client):
    ws = socketio.test_client(app, flask_test_client=client)
    assert ws.is_connected()
    client.post("/api/auth/logout")
    assert not ws.is_connected()


def test_account_switch_revokes_previous_socket(app, client, log_in):
    ws = socketio.test_client(app, flask_test_client=client)
    log_in(client, "samfullstack")
    assert not ws.is_connected()


def test_history_pagination_and_read_cursor_never_moves_backwards(app, client, thread):
    me = Profile.query.filter_by(username="jordan-dev").one()
    rows = [ChatMessage(invite_id=uuid.UUID(thread["id"]), sender_id=me.id,
                        client_token=str(uuid.uuid4()), body=str(i)) for i in range(65)]
    db.session.add_all(rows); db.session.commit()
    url = f"/api/conversations/{thread['id']}"
    latest = client.get(url + "/messages").json
    assert latest["has_more"] and len(latest["messages"]) == 50
    older = client.get(url + f"/messages?before={latest['messages'][0]['id']}").json
    assert not older["has_more"] and len(older["messages"]) == 15
    assert older["messages"][-1]["id"] < latest["messages"][0]["id"]
    assert client.get(url + "/messages?before=nope").status_code == 400
    assert client.post(url + "/read", json={"message_id": 999999}).status_code == 400
    assert client.post(url + "/read", json={"message_id": rows[-1].id}).status_code == 200
    assert client.post(url + "/read", json={"message_id": rows[0].id}).status_code == 200
    db.session.expire_all()
    assert db.session.get(Invite, uuid.UUID(thread["id"])).recipient_read_id == rows[-1].id


def test_idea_generation_uses_profiles_history_and_shares_result(app, client, log_in, thread, monkeypatch):
    app.config["OPENAI_API_KEY"] = "test-only-key"
    ws = socketio.test_client(app, flask_test_client=client)
    ws.emit("chat:send", payload(thread, "Let's build an accessible study app, not a game."), callback=True)
    other = log_in(app.test_client(), thread["sender"]["username"])
    other_ws = socketio.test_client(app, flask_test_client=other)
    other_ws.emit("chat:send", payload(thread, "A two-day MVP with React and Python sounds good."), callback=True)
    captured = []
    def fake_plan(context):
        captured.append(context)
        return {"title": "Study partner", "summary": "An accessible learning app."}
    monkeypatch.setattr(idea_service, "request_plan", fake_plan)
    url = f"/api/conversations/{thread['id']}/ideas"
    result = client.post(url, json={"brief": "No paid hosting"})
    assert result.status_code == 201, result.json
    context = captured[0]
    assert context["brief"] == "No paid hosting"
    assert len(context["profiles"]) == 2
    assert all("skills" in person and "experience_level" in person for person in context["profiles"])
    assert len(context["messages"]) == 2
    assert "accessible study app" in context["messages"][0]["text"]
    assert context["messages"][0]["username"] != context["messages"][1]["username"]
    assert other.get(url).json["ideas"][0]["id"] == result.json["id"]
    assert result.json["context_message_id"] is not None
    assert any(event["name"] == "chat:idea" for event in other_ws.get_received())
    assert client.post(url, json={}).status_code == 429
    assert ProjectIdea.query.count() == 1
    ws.disconnect(); other_ws.disconnect()


def test_idea_configuration_validation_and_provider_failure(app, client, thread, monkeypatch):
    from openai import APIConnectionError
    import httpx
    url = f"/api/conversations/{thread['id']}/ideas"
    app.config["OPENAI_API_KEY"] = ""
    assert client.post(url, json={}).status_code == 503
    app.config["OPENAI_API_KEY"] = "test-only-key"
    assert client.post(url, json={"brief": "x" * 1001}).status_code == 400
    def fail(_):
        raise APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))
    monkeypatch.setattr(idea_service, "request_plan", fail)
    assert client.post(url, json={}).status_code == 502
    assert ProjectIdea.query.count() == 0


def test_deleting_profile_cascades_chat_and_plans(app, client, thread):
    me = Profile.query.filter_by(username="jordan-dev").one()
    db.session.add(ChatMessage(invite_id=uuid.UUID(thread["id"]), sender_id=me.id,
                               client_token=str(uuid.uuid4()), body="Hello"))
    db.session.add(ProjectIdea(invite_id=uuid.UUID(thread["id"]), generated_by=me.id,
                              brief="", content={}, model="test"))
    db.session.commit()
    db.session.delete(me.user); db.session.commit()
    assert ChatMessage.query.count() == 0
    assert ProjectIdea.query.count() == 0


def test_provider_sdk_uses_structured_output_and_does_not_store_requests(app, monkeypatch):
    import json
    from pathlib import Path
    from types import SimpleNamespace
    captured = {}
    plan = idea_service.DesignDocument.model_validate_json(
        Path(__file__).with_name("fixtures").joinpath("project_plan.json").read_text())
    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_parsed=plan)
    monkeypatch.setattr(idea_service, "OpenAI", FakeClient)
    context = {"profiles": [{"username": "one"}, {"username": "two"}], "messages": [{"text": "Study planner"}]}
    result = idea_service.request_plan(context)
    assert result["title"] == "StudySprint"
    assert captured["store"] is False
    assert captured["text_format"] is idea_service.DesignDocument
    assert json.loads(captured["input"]) == context


def test_quota_error_is_actionable_and_does_not_save_a_fake_plan(app, client, thread, monkeypatch):
    import httpx
    from openai import RateLimitError
    app.config["OPENAI_API_KEY"] = "test-only-key"
    def fail(_):
        response = httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
        raise RateLimitError("No credits remaining", response=response, body={"code": "insufficient_quota"})
    monkeypatch.setattr(idea_service, "request_plan", fail)
    response = client.post(f"/api/conversations/{thread['id']}/ideas", json={})
    assert response.status_code == 503
    assert "credits" in response.json["error"]["message"]
    assert ProjectIdea.query.count() == 0


def test_idea_context_is_bounded_and_preserves_latest_decisions(app, client, thread):
    me = Profile.query.filter_by(username="jordan-dev").one()
    invite = db.session.get(Invite, uuid.UUID(thread["id"]))
    db.session.add_all([ChatMessage(invite_id=invite.id, sender_id=me.id, client_token=str(uuid.uuid4()),
                                    body="x" * 2000) for _ in range(110)])
    db.session.add(ChatMessage(invite_id=invite.id, sender_id=me.id, client_token=str(uuid.uuid4()),
                               body="Final decision: a small study planner, no payments."))
    db.session.commit()
    context, last_id = idea_service.build_context(invite, "Two days")
    assert sum(len(message["text"]) for message in context["messages"]) <= 24000
    assert len(context["messages"]) <= 100
    assert "Final decision" in context["messages"][-1]["text"]
    assert last_id == ChatMessage.query.order_by(ChatMessage.id.desc()).first().id
