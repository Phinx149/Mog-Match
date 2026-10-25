from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from types import SimpleNamespace
import uuid

import httpx
import pytest
from openai import APIConnectionError

from app.extensions import db, socketio
from app.models import ChatMessage, Invite, Profile, ProjectIdea, StudioTurn
from app.services import idea_service, studio_service


@pytest.fixture
def studio(app, client):
    app.config["OPENAI_API_KEY"] = "test-only-key"
    invite = client.get("/api/invites/inbox").json["received"][0]
    client.patch(f"/api/invites/{invite['id']}", json={"status": "accepted"})
    me = Profile.query.filter_by(username="jordan-dev").one()
    content = json.loads(Path(__file__).with_name("fixtures").joinpath("project_plan.json").read_text())
    base = ProjectIdea(invite_id=uuid.UUID(invite["id"]), generated_by=me.id, content=content, model="test")
    newer = ProjectIdea(invite_id=uuid.UUID(invite["id"]), generated_by=me.id,
                        content={**content, "title": "A different newer idea"}, model="test")
    db.session.add(base); db.session.flush(); db.session.add(newer); db.session.commit()
    return SimpleNamespace(invite=invite, base=base, newer=newer,
                           url=f"/api/conversations/{invite['id']}/ideas/{base.id}/assistant")


def request(mode="ask", prompt="Why this architecture?", token=None):
    return {"mode": mode, "prompt": prompt, "client_token": token or str(uuid.uuid4())}


def proposed(studio):
    return idea_service.DesignDocument.model_validate({**studio.base.content, "title": "StudySprint Weekend",
        "features": ["Create a study goal", "Track completion"],
        "architecture": "A single Flask app serves the React client and stores goals in SQLite."})


def age_turns():
    StudioTurn.query.update({"created_at": datetime.now(timezone.utc) - timedelta(seconds=10)})
    db.session.commit()


def test_questions_use_selected_version_not_newest_and_do_not_publish(client, studio, monkeypatch):
    captured = []
    def answer(context):
        captured.append(context)
        return studio_service.StudioReply(answer="React fits your shared skills and Flask keeps the API small.",
                                           change_summary=[], proposal=None)
    monkeypatch.setattr(studio_service, "request_reply", answer)
    first = client.post(studio.url, json=request())
    assert first.status_code == 201, first.json
    assert first.json["proposal"] is None
    assert ProjectIdea.query.count() == 2
    assert captured[0]["selected_document"]["title"] == "StudySprint"
    assert "previous_plan" not in captured[0]
    assert len(captured[0]["profiles"]) == 2
    assert captured[0]["asked_by"] == "jordan-dev"
    age_turns()
    assert client.post(studio.url, json=request(prompt="What are the tradeoffs?")).status_code == 201
    assert len(captured[1]["studio_history"]) == 1
    assert captured[1]["studio_history"][0]["question"] == "Why this architecture?"
    assert len(client.get(studio.url).json["turns"]) == 2
    assert client.post(studio.url + f"/{first.json['id']}/apply").status_code == 400


def test_revision_is_preview_until_applied_shared_and_idempotent(app, client, log_in, studio, monkeypatch):
    monkeypatch.setattr(studio_service, "request_reply", lambda context: studio_service.StudioReply(
        answer="Here is a smaller weekend proposal.", change_summary=["Simplify the architecture.", "Reduce the MVP scope."],
        proposal=proposed(studio)))
    other = log_in(app.test_client(), studio.invite["sender"]["username"])
    other_ws = socketio.test_client(app, flask_test_client=other)
    outsider = log_in(app.test_client(), "samfullstack")
    outsider_ws = socketio.test_client(app, flask_test_client=outsider)
    original = dict(studio.base.content)
    response = client.post(studio.url, json=request("revise", "Simplify this into a weekend MVP."))
    assert response.status_code == 201, response.json
    turn = response.json
    assert turn["proposal"]["title"] == "StudySprint Weekend"
    assert turn["saved_idea_id"] is None
    assert ProjectIdea.query.count() == 2 and studio.base.content == original
    assert other.get(studio.url).json["turns"][0]["id"] == turn["id"]
    assert any(event["name"] == "chat:studio" for event in other_ws.get_received())
    assert outsider_ws.get_received() == []
    # Either collaborator can apply the exact shared preview. Applying never calls the provider.
    monkeypatch.setattr(studio_service, "request_reply", lambda _: pytest.fail("Apply called the AI"))
    applied = other.post(studio.url + f"/{turn['id']}/apply")
    assert applied.status_code == 201, applied.json
    assert applied.json["idea"]["content"] == turn["proposal"]
    assert applied.json["idea"]["parent_idea_id"] == str(studio.base.id)
    assert applied.json["idea"]["generated_by"] == studio.invite["sender"]["id"]
    assert applied.json["turn"]["saved_idea_id"] == applied.json["idea"]["id"]
    assert ProjectIdea.query.count() == 3
    assert studio.base.content == original
    assert client.post(studio.url + f"/{turn['id']}/apply").status_code == 200
    assert ProjectIdea.query.count() == 3
    assert any(event["name"] == "chat:idea" for event in other_ws.get_received())
    assert outsider_ws.get_received() == []
    other_ws.disconnect(); outsider_ws.disconnect()


def test_duplicate_ai_request_token_does_not_spend_again(app, client, studio, monkeypatch):
    calls = []
    def answer(context):
        calls.append(context)
        return studio_service.StudioReply(answer="An explanation", change_summary=[], proposal=None)
    monkeypatch.setattr(studio_service, "request_reply", answer)
    data = request()
    first = client.post(studio.url, json=data)
    app.config["OPENAI_API_KEY"] = ""
    retry = client.post(studio.url, json=data)
    assert retry.status_code == 201 and retry.json == first.json
    assert len(calls) == 1 and StudioTurn.query.count() == 1


def test_ai_cannot_accidentally_turn_a_question_into_a_revision(client, studio, monkeypatch):
    monkeypatch.setattr(studio_service, "request_reply", lambda _: studio_service.StudioReply(
        answer="Explanation", change_summary=["Unrequested change"], proposal=proposed(studio)))
    result = client.post(studio.url, json=request()).json
    assert result["proposal"] is None and result["change_summary"] == []
    assert client.post(studio.url + f"/{result['id']}/apply").status_code == 400
    assert ProjectIdea.query.count() == 2


def test_studio_access_is_restricted_to_accepted_conversation_members(app, client, log_in, anon_client, studio):
    assert anon_client.get(studio.url).status_code == 401
    outsider = log_in(app.test_client(), "samfullstack")
    assert outsider.get(studio.url).status_code == 404
    assert outsider.post(studio.url, json=request()).status_code == 404
    assert outsider.post(studio.url + "/1/apply").status_code == 404
    # An idea ID from another conversation cannot be used even when the caller is in both.
    me = Profile.query.filter_by(username="jordan-dev").one()
    sam = Profile.query.filter_by(username="samfullstack").one()
    other = Invite(sender_id=me.id, recipient_id=sam.id, status="accepted")
    db.session.add(other); db.session.commit()
    wrong_url = f"/api/conversations/{other.id}/ideas/{studio.base.id}/assistant"
    assert client.get(wrong_url).status_code == 404
    invite = db.session.get(Invite, uuid.UUID(studio.invite["id"]))
    invite.status = "pending"; db.session.commit()
    assert client.get(studio.url).status_code == 404


@pytest.mark.parametrize("patch", [{"mode": "bad"}, {"prompt": " "}, {"prompt": None},
                                    {"prompt": "x" * 2001}, {"client_token": "bad"}, {"author_id": "spoofed"}])
def test_studio_validation(client, studio, patch):
    result = client.post(studio.url, json={**request(), **patch})
    assert result.status_code == 400
    assert StudioTurn.query.count() == 0


def test_missing_key_provider_failure_and_cooldown_do_not_modify_the_doc(app, client, studio, monkeypatch):
    app.config["OPENAI_API_KEY"] = ""
    assert client.post(studio.url, json=request()).status_code == 503
    app.config["OPENAI_API_KEY"] = "test-only-key"
    def fail(_):
        raise APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))
    monkeypatch.setattr(studio_service, "request_reply", fail)
    assert client.post(studio.url, json=request()).status_code == 502
    assert StudioTurn.query.count() == 0 and ProjectIdea.query.count() == 2
    monkeypatch.setattr(studio_service, "request_reply", lambda _: studio_service.StudioReply(
        answer="Answer", change_summary=[], proposal=None))
    assert client.post(studio.url, json=request()).status_code == 201
    assert client.post(studio.url, json=request()).status_code == 429
    assert StudioTurn.query.count() == 1


def test_revision_without_proposal_does_not_create_a_turn(client, studio, monkeypatch):
    monkeypatch.setattr(studio_service, "request_reply", lambda _: studio_service.StudioReply(
        answer="Couldn't revise", change_summary=[], proposal=None))
    assert client.post(studio.url, json=request("revise")).status_code == 502
    assert StudioTurn.query.count() == 0


def test_two_collaborators_applying_simultaneously_create_one_version(app, client, studio, monkeypatch):
    monkeypatch.setattr(studio_service, "request_reply", lambda _: studio_service.StudioReply(
        answer="Preview", change_summary=["Smaller MVP"], proposal=proposed(studio)))
    turn = client.post(studio.url, json=request("revise")).json
    url = studio.url + f"/{turn['id']}/apply"
    names = ["jordan-dev", studio.invite["sender"]["username"]]
    def apply_as(username):
        with app.app_context():
            session_client = app.test_client()
            assert session_client.post("/api/auth/login", json={"username": username, "password": app.config["SEED_PASSWORD"]}).status_code == 200
            response = session_client.post(url)
            return response.status_code, response.json["idea"]["id"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(apply_as, names))
    assert sorted(status for status, _ in results) == [200, 201]
    assert results[0][1] == results[1][1]
    assert ProjectIdea.query.count() == 3


def test_pagination_and_context_are_scoped_and_bounded(client, studio, monkeypatch):
    me = Profile.query.filter_by(username="jordan-dev").one()
    for i in range(35):
        db.session.add(StudioTurn(idea_id=studio.base.id, author_id=me.id, client_token=str(uuid.uuid4()),
                                  mode="ask", prompt=f"Question {i}", answer="a" * 1500, model="test"))
    db.session.commit(); age_turns()
    page = client.get(studio.url).json
    assert page["has_more"] and len(page["turns"]) == 30
    earlier = client.get(studio.url + f"?before={page['turns'][0]['id']}").json
    assert not earlier["has_more"] and len(earlier["turns"]) == 5
    assert client.get(studio.url + "?before=bad").status_code == 400
    captured = []
    def answer(context):
        captured.append(context)
        return studio_service.StudioReply(answer="Answer", change_summary=[], proposal=None)
    monkeypatch.setattr(studio_service, "request_reply", answer)
    assert client.post(studio.url, json=request()).status_code == 201
    history = captured[0]["studio_history"]
    assert len(history) <= 20
    assert sum(len(row["question"]) + len(row["answer"]) for row in history) <= 12000
    assert history[-1]["question"] == "Question 34"


def test_structured_provider_reply_and_refusal(app, monkeypatch):
    captured = {}
    class FakeClient:
        def __init__(self, **kwargs): self.responses = self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_parsed=studio_service.StudioReply(answer="Explanation", change_summary=[], proposal=None))
    monkeypatch.setattr(studio_service, "OpenAI", FakeClient)
    context = {"selected_document": {"title": "Older version"}, "mode": "ask", "prompt": "Why?"}
    assert studio_service.request_reply(context).proposal is None
    assert captured["store"] is False
    assert captured["text_format"] is studio_service.StudioReply
    assert json.loads(captured["input"]) == context


def test_deleting_source_cascades_studio_history_and_preserves_saved_version(client, studio, monkeypatch):
    monkeypatch.setattr(studio_service, "request_reply", lambda _: studio_service.StudioReply(
        answer="Preview", change_summary=["Smaller MVP"], proposal=proposed(studio)))
    turn = client.post(studio.url, json=request("revise")).json
    saved = client.post(studio.url + f"/{turn['id']}/apply").json["idea"]
    db.session.delete(studio.base); db.session.commit(); db.session.expire_all()
    assert StudioTurn.query.count() == 0
    assert db.session.get(ProjectIdea, uuid.UUID(saved["id"])).parent_idea_id is None
