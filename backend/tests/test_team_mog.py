from copy import deepcopy

import pytest

from app.extensions import socketio
from app.services.mog_score import compute_mog_score
from app.services.team_mog import compute_team_mog


def profile(identity="a", **overrides):
    data = {"id": identity, "full_name": identity.upper(), "username": identity, "avatar_url": None,
            "location": None, "education": None, "bio": "", "favorite_ide": None,
            "favorite_ai_agents": [], "skills": [], "interests": [], "experience_level": None,
            "looking_for": [], "links": [], "projects": []}
    return {**data, **overrides}


def row(result, key):
    return next(item for item in result["breakdown"] if item["key"] == key)


def test_empty_profiles_do_not_earn_unfounded_team_points():
    score = compute_team_mog(profile(), profile("b"))
    assert score["score"] == 0 and score["max_score"] == 1000
    assert len(score["breakdown"]) == 5
    assert all(item["points"] == 0 and item["reason"] for item in score["breakdown"])


def test_team_score_is_symmetric_deterministic_and_explained():
    a = profile(skills=["Frontend", "React", "TypeScript"], looking_for=["Side project"], experience_level="Junior")
    b = profile("b", skills=["Backend", "Python", "React"], looking_for=["Side project"], experience_level="Mid-level")
    snapshot = deepcopy([a, b])
    score = compute_team_mog(a, b)
    assert score == compute_team_mog(b, a) == compute_team_mog(a, b)
    assert [a, b] == snapshot
    assert score["score"] == sum(item["points"] for item in score["breakdown"])
    assert sum(item["max"] for item in score["breakdown"]) == 1000
    assert all(0 <= item["points"] <= item["max"] and item["reason"] for item in score["breakdown"])
    assert row(score, "strength")["points"] == round((compute_mog_score(a)["score"] + compute_mog_score(b)["score"]) * 2)
    assert row(score, "coverage")["points"] == 100
    assert row(score, "ground")["points"] == 100


def test_complementary_pair_outscores_clones_with_equal_individual_scores():
    a = profile(skills=["Frontend", "React", "TypeScript"], experience_level="Junior")
    clone = profile("b", skills=a["skills"], experience_level="Junior")
    complement = profile("b", skills=["Backend", "Python", "React"], experience_level="Junior")
    assert compute_mog_score(clone)["score"] == compute_mog_score(complement)["score"]
    assert compute_team_mog(a, complement)["score"] > compute_team_mog(a, clone)["score"]


def test_aliases_and_duplicate_specialties_do_not_inflate_coverage():
    a = profile(skills=["Frontend", "frontend", " React ", "JS"])
    b = profile("b", skills=["Backend", "React", "JavaScript"])
    result = compute_team_mog(a, b)
    assert row(result, "coverage")["points"] == 100
    assert "2 shared" in row(result, "complementarity")["reason"]


@pytest.mark.parametrize("level_a,level_b,goals_a,goals_b,expected", [
    ("Student", "Lead", [], [], 0),
    ("Student", "Lead", ["Mentor"], ["Mentee"], 50),
    ("Junior", "Mid-level", [], [], 50),
    (None, "Lead", ["Mentor"], ["Mentee"], 0),
])
def test_experience_balance_and_mentorship(level_a, level_b, goals_a, goals_b, expected):
    score = compute_team_mog(profile(experience_level=level_a, looking_for=goals_a),
                             profile("b", experience_level=level_b, looking_for=goals_b))
    assert row(score, "balance")["points"] == expected


def test_missing_skills_do_not_gain_complementarity_and_coverage_is_capped():
    a = profile(skills=["Frontend", "Backend", "Mobile", "DevOps", "Cloud", "Security"])
    score = compute_team_mog(a, profile("b"))
    assert row(score, "coverage")["points"] == 250
    assert row(score, "complementarity")["points"] == 0
    assert 0 <= score["score"] <= 1000


def test_acceptance_saves_same_snapshot_for_both_and_only_notifies_participants(app, client, log_in):
    received = client.get("/api/invites/inbox").json["received"][0]
    assert received["team_mog"] is None
    other = log_in(app.test_client(), received["sender"]["username"])
    outsider = log_in(app.test_client(), "samfullstack")
    sockets = [socketio.test_client(app, flask_test_client=session) for session in (client, other, outsider)]
    response = client.patch(f"/api/invites/{received['id']}", json={"status": "accepted"})
    assert response.status_code == 200, response.json
    score = response.json["team_mog"]
    assert score and score["score"] == sum(item["points"] for item in score["breakdown"])
    assert {member["id"] for member in score["members"]} == {received["sender"]["id"], received["recipient"]["id"]}
    for ws in sockets[:2]:
        events = [event for event in ws.get_received() if event["name"] == "team:matched"]
        assert len(events) == 1 and events[0]["args"][0]["team_mog"] == score
    assert sockets[2].get_received() == []
    assert other.get("/api/invites/inbox").json["sent"][0]["team_mog"] == score
    # Updating either profile doesn't retroactively change the accepted-match result.
    client.patch("/api/profiles/me", json={"skills": ["Haskell", "Backend", "Frontend"]})
    saved = next(invite for invite in client.get("/api/invites/inbox").json["received"] if invite["id"] == received["id"])
    assert saved["team_mog"] == score
    assert client.patch(f"/api/invites/{received['id']}", json={"status": "accepted"}).status_code == 409
    for ws in sockets: ws.disconnect()


def test_decline_does_not_create_or_broadcast_a_team_score(app, client):
    invite = client.get("/api/invites/inbox").json["received"][0]
    ws = socketio.test_client(app, flask_test_client=client)
    response = client.patch(f"/api/invites/{invite['id']}", json={"status": "declined"})
    assert response.status_code == 200 and response.json["team_mog"] is None
    assert not any(event["name"] == "team:matched" for event in ws.get_received())
    ws.disconnect()
