from app.services.mog_match import WEIGHTS, compute_match, rank_matches


def make_profile(**overrides):
    profile = {
        "skills": [],
        "interests": [],
        "looking_for": [],
        "experience_level": None,
        "favorite_ai_agents": [],
        "favorite_ide": None,
        "location": None,
        "projects": [],
    }
    profile.update(overrides)
    return profile


def project(technologies):
    return {"title": "Thing", "description": "", "project_url": None, "technologies": list(technologies)}


ME = make_profile(
    skills=["Python", "React", "Flask", "TypeScript", "PostgreSQL"],
    interests=["Hackathons", "AI", "Startups"],
    looking_for=["Hackathon team", "Mentor"],
    experience_level="Student",
    favorite_ai_agents=["Claude Code", "GitHub Copilot"],
    favorite_ide="VS Code",
    location="Austin, TX",
)


def test_weights_add_up_to_100():
    assert sum(WEIGHTS.values()) == 100


def test_identical_profile_is_a_perfect_match():
    twin = {**ME, "looking_for": ["Hackathon team", "Mentee"]}  # Mentor pairs with Mentee
    result = compute_match(ME, twin)
    assert result["score"] == 100
    assert result["label"] == "Basically your twin"
    assert result["breakdown"] == WEIGHTS


def test_empty_profiles_share_nothing():
    result = compute_match(make_profile(), make_profile())
    assert result["score"] == 0
    assert result["label"] == "Total strangers"
    assert result["shared"] == {"skills": [], "interests": [], "looking_for": [], "ai_agents": []}


def test_comparison_ignores_case_and_reports_their_spelling():
    other = make_profile(skills=["python", "Go"], interests=["ai"], favorite_ide="vs code")
    result = compute_match(ME, other)
    assert result["shared"]["skills"] == ["python"]
    assert result["shared"]["interests"] == ["ai"]
    assert result["breakdown"]["ide"] == WEIGHTS["ide"]


def test_project_technologies_count_as_skills():
    other = make_profile(projects=[project(["Flask", "React"])])
    result = compute_match(ME, other)
    assert result["shared"]["skills"] == ["Flask", "React"]
    assert result["breakdown"]["skills"] > 0


def test_mentor_matches_mentee_as_well_as_another_mentor():
    mentee = compute_match(ME, make_profile(looking_for=["Mentee"]))
    mentor = compute_match(ME, make_profile(looking_for=["Mentor"]))
    assert mentee["shared"]["looking_for"] == ["Mentee"]
    assert mentor["shared"]["looking_for"] == ["Mentor"]


def test_every_seeded_profile_is_a_100_match_with_an_exact_copy(client):
    # The guarantee: same profile -> 100, whatever its list lengths or goals.
    profiles = client.get("/api/profiles").get_json()["profiles"] + [client.get("/api/profiles/me").get_json()]
    for profile in profiles:
        result = compute_match(profile, dict(profile))
        assert result["score"] == 100, (profile["username"], result["breakdown"])


def test_short_identical_lists_still_get_full_points():
    one_agent = make_profile(skills=["Go"], interests=["AI"], looking_for=["Mentor"], favorite_ai_agents=["Cursor"])
    breakdown = compute_match(one_agent, dict(one_agent))["breakdown"]
    assert breakdown["skills"] == WEIGHTS["skills"]
    assert breakdown["ai_agents"] == WEIGHTS["ai_agents"]
    assert breakdown["looking_for"] == WEIGHTS["looking_for"]


def test_one_shared_skill_is_not_full_points_when_either_lists_more():
    breakdown = compute_match(ME, make_profile(skills=["Python"]))["breakdown"]
    assert breakdown["skills"] == round(WEIGHTS["skills"] / 5)


def test_experience_gives_half_points_one_level_apart():
    assert compute_match(ME, make_profile(experience_level="Junior"))["breakdown"]["experience"] == 5
    assert compute_match(ME, make_profile(experience_level="Lead"))["breakdown"]["experience"] == 0


def test_rank_matches_puts_most_similar_first():
    stranger = make_profile(skills=["COBOL"])
    close = make_profile(skills=["Python", "React"], interests=["AI"])
    ranked = rank_matches(ME, [stranger, close])
    assert [p["skills"] for p in ranked] == [close["skills"], stranger["skills"]]
    assert ranked[0]["match"]["score"] > ranked[1]["match"]["score"]


def test_shared_tech_and_interests_beat_shared_goals_and_level():
    # Regression: goals + experience used to outrank someone with a much closer stack.
    same_goals = make_profile(skills=["Rust"], looking_for=["Hackathon team", "Mentee"], experience_level="Student")
    same_stack = make_profile(skills=["Python", "React", "Flask"], interests=["Startups"])
    assert compute_match(ME, same_stack)["score"] > compute_match(ME, same_goals)["score"]


def test_long_skill_lists_do_not_water_down_overlap():
    other = make_profile(skills=["Python", "React"])
    padded = {**ME, "skills": ME["skills"] + ["Go", "Rust", "C", "Java", "Ruby", "Swift"]}
    assert compute_match(padded, other)["breakdown"]["skills"] == compute_match(ME, other)["breakdown"]["skills"]


def test_same_input_same_output():
    other = make_profile(skills=["Python"], interests=["AI"])
    assert compute_match(ME, other) == compute_match(ME, other)
