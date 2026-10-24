from app.services.mog_score import WEIGHTS, compute_mog_score


def make_profile(**overrides):
    profile = {
        "avatar_url": None,
        "location": None,
        "education": None,
        "bio": "",
        "favorite_ide": None,
        "favorite_ai_agents": [],
        "skills": [],
        "interests": [],
        "experience_level": None,
        "looking_for": [],
        "links": [],
        "projects": [],
    }
    profile.update(overrides)
    return profile


def project(technologies=(), description="", url=None):
    return {"title": "Thing", "description": description, "project_url": url, "technologies": list(technologies)}


ARCANE = ["COBOL", "Fortran", "Ada", "Assembly", "Prolog"]
MAXED = make_profile(
    avatar_url="https://example.com/a.png",
    location="Berlin",
    education="MIT",
    bio="x" * 500,
    favorite_ide="Emacs",
    favorite_ai_agents=["Claude Code"],
    skills=ARCANE + ["Lisp", "Verilog", "VHDL", "Pascal", "Haskell"],
    interests=["Retro computing", "Compilers"],
    experience_level="Lead",
    looking_for=["Hackathon team"],
    links=[{"label": "GitHub", "url": "https://github.com/x"}] * 3,
    projects=[project(ARCANE, "y" * 600, "https://example.com")] * 3,
)


def test_weights_add_up_to_100():
    assert sum(WEIGHTS.values()) == 100


def test_empty_profile_scores_low_with_tips():
    result = compute_mog_score(make_profile())
    assert result["score"] < 5 and result["tier"] == "Hello World"
    assert len(result["tips"]) == 3


def test_maxed_profile_is_exactly_100_and_gigamogger():
    result = compute_mog_score(MAXED)
    assert result["score"] == 100
    assert result["tier"] == "Gigamogger"
    assert result["breakdown"] == WEIGHTS
    assert result["tips"] == []


def test_esoteric_languages_beat_mainstream_ones():
    weird = compute_mog_score(make_profile(projects=[project(["Haskell", "Zig"])]))
    normal = compute_mog_score(make_profile(projects=[project(["Python", "JavaScript"])]))
    assert weird["breakdown"]["esoteric"] > normal["breakdown"]["esoteric"]


def test_language_used_in_a_project_counts_double_a_listed_skill():
    listed = compute_mog_score(make_profile(skills=["COBOL"]))
    used = compute_mog_score(make_profile(projects=[project(["COBOL"])]))
    assert used["breakdown"]["esoteric"] == 2 * listed["breakdown"]["esoteric"] == 10


def test_frameworks_are_not_languages():
    result = compute_mog_score(make_profile(skills=["React", "Docker", "Frontend"]))
    assert result["breakdown"]["esoteric"] == 0


def test_language_matching_ignores_case():
    result = compute_mog_score(make_profile(skills=["cobol"]))
    assert result["breakdown"]["esoteric"] == 5


def test_longer_descriptions_score_higher():
    short = compute_mog_score(make_profile(projects=[project(description="it does stuff")]))
    long = compute_mog_score(make_profile(projects=[project(description="a" * 300)]))
    assert short["breakdown"]["descriptions"] < long["breakdown"]["descriptions"]


def test_counts_are_capped():
    result = compute_mog_score(
        make_profile(links=[{"label": "x", "url": "https://x.dev"}] * 9, projects=[project()] * 9)
    )
    assert result["breakdown"]["links"] == WEIGHTS["links"]
    assert result["breakdown"]["projects"] == WEIGHTS["projects"]


def test_same_input_same_output():
    assert compute_mog_score(MAXED) == compute_mog_score(MAXED)


def test_api_includes_mog_score(client):
    body = client.get("/api/profiles/me").get_json()
    assert 0 <= body["mog"]["score"] <= 100
    assert set(body["mog"]["breakdown"]) == set(WEIGHTS)


def test_discover_sort_and_min_tier(client):
    profiles = client.get("/api/profiles?sort=mog").get_json()["profiles"]
    scores = [p["mog"]["score"] for p in profiles]
    assert scores == sorted(scores, reverse=True)

    filtered = client.get("/api/profiles?min_tier=Mid%20Mogger").get_json()["profiles"]
    assert all(p["mog"]["score"] >= 45 for p in filtered)


def test_discover_rejects_unknown_tier(client):
    response = client.get("/api/profiles?min_tier=Sigma")
    assert response.status_code == 400
    assert "min_tier" in response.get_json()["error"]["fields"]


def test_listing_arcane_languages_cannot_max_esoteric():
    faker = compute_mog_score(make_profile(skills=ARCANE * 2 + ["Lisp", "Verilog", "VHDL", "Pascal"]))
    shipper = compute_mog_score(make_profile(projects=[project(ARCANE)]))
    assert faker["breakdown"]["esoteric"] <= WEIGHTS["esoteric"] // 2
    assert shipper["breakdown"]["esoteric"] == WEIGHTS["esoteric"]
