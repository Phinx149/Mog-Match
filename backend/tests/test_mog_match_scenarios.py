"""Mog Match across many situations: edge cases, symmetry, bounds and the real seeded data."""

import itertools

import pytest

from app.services.mog_match import WEIGHTS, compute_match


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


def project(*technologies):
    return {"title": "Thing", "description": "", "project_url": None, "technologies": list(technologies)}


FULL = make_profile(
    skills=["Python", "React", "Flask", "TypeScript", "PostgreSQL", "Docker"],
    interests=["AI", "Startups", "Hackathons", "Music"],
    looking_for=["Hackathon team", "Side project"],
    experience_level="Mid-level",
    favorite_ai_agents=["Claude Code", "Cursor"],
    favorite_ide="VS Code",
    location="Austin, TX",
    projects=[project("React", "Flask")],
)


# ---------- the score for specific situations ----------

@pytest.mark.parametrize(
    ("name", "me", "other", "expected"),
    [
        ("both empty", make_profile(), make_profile(), 0),
        ("full vs empty", FULL, make_profile(), 0),
        ("identical", FULL, FULL, 100),
        ("identical, different capitalisation",
         FULL,
         {**FULL, "skills": [s.upper() for s in FULL["skills"]], "interests": [i.lower() for i in FULL["interests"]],
          "favorite_ide": "vs code", "location": "AUSTIN, TX"},
         100),
        ("nothing in common", FULL,
         make_profile(skills=["COBOL"], interests=["Golf"], looking_for=["Cofounder"], experience_level="Lead",
                      favorite_ai_agents=["Copilot"], favorite_ide="Emacs", location="Oslo"),
         0),
        ("only same location", FULL, make_profile(location="austin, tx"), WEIGHTS["location"]),
        ("only same IDE", FULL, make_profile(favorite_ide="VS Code"), WEIGHTS["ide"]),
        ("only same level", FULL, make_profile(experience_level="Mid-level"), WEIGHTS["experience"]),
        ("level one apart", FULL, make_profile(experience_level="Senior"), WEIGHTS["experience"] // 2),
        ("level two apart", FULL, make_profile(experience_level="Lead"), 0),
        ("one shared skill of 5", FULL, make_profile(skills=["Python"]), 9),
        ("five shared skills = full", FULL, make_profile(skills=["Python", "React", "Flask", "TypeScript", "Docker"]),
         WEIGHTS["skills"]),
        ("more than five shared still capped", FULL, make_profile(skills=FULL["skills"]), WEIGHTS["skills"]),
        ("shared tech only via their project", FULL, make_profile(projects=[project("Docker", "PostgreSQL")]), 18),
        ("one shared interest of 3", FULL, make_profile(interests=["Music"]), 8),
        ("one shared goal of 2", FULL, make_profile(looking_for=["Side project"]), 5),
    ],
)
def test_score_for_situation(name, me, other, expected):
    assert compute_match(me, other)["score"] == expected, name


def test_unknown_or_missing_experience_scores_nothing():
    for level in [None, "", "Wizard"]:
        assert compute_match(FULL, make_profile(experience_level=level))["breakdown"]["experience"] == 0


def test_blank_ide_or_location_never_counts_as_the_same():
    a = make_profile(favorite_ide="", location="  ")
    assert compute_match(a, dict(a))["score"] == 0


def test_duplicate_spellings_count_once():
    me = make_profile(skills=["React", "react", "REACT"])
    other = make_profile(skills=["React"])
    result = compute_match(me, other)
    assert result["shared"]["skills"] == ["React"]
    assert result["breakdown"]["skills"] == WEIGHTS["skills"]  # both really list just one skill


def test_mentor_and_mentee_goals():
    mentor_seeker = make_profile(looking_for=["Mentor"])
    assert compute_match(mentor_seeker, make_profile(looking_for=["Mentee"]))["shared"]["looking_for"] == ["Mentee"]
    assert compute_match(mentor_seeker, make_profile(looking_for=["Mentor"]))["shared"]["looking_for"] == ["Mentor"]
    assert compute_match(mentor_seeker, make_profile(looking_for=["Cofounder"]))["shared"]["looking_for"] == []


def test_short_lists_reach_full_points_only_when_everything_is_shared():
    one_agent = make_profile(favorite_ai_agents=["Cursor"])
    assert compute_match(one_agent, one_agent)["breakdown"]["ai_agents"] == WEIGHTS["ai_agents"]
    # They list two, I list one: sharing one of their two is half.
    two_agents = make_profile(favorite_ai_agents=["Cursor", "Claude Code"])
    assert compute_match(one_agent, two_agents)["breakdown"]["ai_agents"] == round(WEIGHTS["ai_agents"] / 2)


def test_adding_a_shared_skill_never_lowers_the_score():
    other = make_profile(skills=[])
    previous = compute_match(FULL, other)["score"]
    for skill in FULL["skills"]:
        other = {**other, "skills": other["skills"] + [skill]}
        score = compute_match(FULL, other)["score"]
        assert score >= previous
        previous = score


def test_labels_follow_the_score():
    assert compute_match(FULL, FULL)["label"] == "Basically your twin"
    assert compute_match(make_profile(), make_profile())["label"] == "Total strangers"


# ---------- properties over every pair of real seeded profiles ----------

@pytest.fixture
def seeded(client):
    return client.get("/api/profiles").get_json()["profiles"] + [client.get("/api/profiles/me").get_json()]


def test_every_pair_is_in_bounds_symmetric_and_explained(seeded):
    for a, b in itertools.combinations(seeded, 2):
        ab, ba = compute_match(a, b), compute_match(b, a)
        pair = (a["username"], b["username"])
        assert 0 <= ab["score"] <= 100, pair
        assert ab["score"] == ba["score"], pair  # A vs B = B vs A
        assert ab["score"] == sum(ab["breakdown"].values()), pair
        assert all(0 <= ab["breakdown"][k] <= WEIGHTS[k] for k in WEIGHTS), pair
        assert ab["score"] < 100, pair  # no two different seeded people are twins


def test_every_seeded_profile_is_its_own_twin(seeded):
    for profile in seeded:
        assert compute_match(profile, dict(profile))["score"] == 100, profile["username"]


def test_shared_items_are_really_on_both_profiles(seeded):
    for a, b in itertools.permutations(seeded, 2):
        shared = compute_match(a, b)["shared"]
        a_stack = {t.lower() for t in a["skills"] + [t for p in a["projects"] for t in p["technologies"]]}
        assert all(skill.lower() in a_stack for skill in shared["skills"])
        assert all(interest in b["interests"] for interest in shared["interests"])
        assert all(agent in b["favorite_ai_agents"] for agent in shared["ai_agents"])
