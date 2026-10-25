"""Mog Match: how similar another developer is to you, 0-100. See docs/MOG_MATCH.md.

Pure functions only, like mog_score.py: they take two dicts from `profile_service.to_dict`
and return a plain dict. No DB, HTTP, clock or randomness, so the same pair always gets
the same result.
"""

from typing import Any

# Max points per component. They add up to 100; tune here. Tech stack and interests carry
# most of the weight: they're what makes two devs alike. Goals come from a short fixed list
# that almost everyone shares a little of, so they only nudge the ranking.
WEIGHTS: dict[str, int] = {
    "skills": 45,
    "interests": 24,
    "looking_for": 10,
    "experience": 10,
    "ai_agents": 5,
    "ide": 3,
    "location": 3,
}

# How many shared items earn a list component full points; each shared item is worth an
# equal slice. We count shared items instead of dividing by the combined list size, so a
# long skill list can't water down real overlap. If both lists are shorter than this, sharing
# all of the longer one is enough, so an identical profile always gets full points.
FULL_AT: dict[str, int] = {
    "skills": 5,
    "interests": 3,
    "looking_for": 2,
    "ai_agents": 2,
}

EXPERIENCE_ORDER = ["Student", "Junior", "Mid-level", "Senior", "Lead"]

# Someone looking for a Mentor also matches someone looking for a Mentee (and vice versa),
# on top of the usual "same goal" match.
COMPLEMENTARY_GOALS = {"mentor": "mentee", "mentee": "mentor"}

# (min score, label), highest first.
LABELS = [
    (80, "Basically your twin"),
    (60, "Same wavelength"),
    (40, "Solid common ground"),
    (20, "A few things in common"),
    (0, "Total strangers"),
]


def compute_match(me: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    my_stack, their_stack = _tech_stack(me), _tech_stack(other)
    my_goals = _lower_set(me["looking_for"])
    # In the other person's spelling, so the UI can show them as they appear on their card.
    shared = {
        "skills": _shared(my_stack, their_stack),
        "interests": _shared(me["interests"], other["interests"]),
        "looking_for": [goal for goal in other["looking_for"]
                        if goal.lower() in my_goals or COMPLEMENTARY_GOALS.get(goal.lower()) in my_goals],
        "ai_agents": _shared(me["favorite_ai_agents"], other["favorite_ai_agents"]),
    }
    sizes = {
        "skills": (my_stack, their_stack),
        "interests": (me["interests"], other["interests"]),
        "looking_for": (me["looking_for"], other["looking_for"]),
        "ai_agents": (me["favorite_ai_agents"], other["favorite_ai_agents"]),
    }
    points = {key: _shared_points(shared[key], key, *lists) for key, lists in sizes.items()}

    breakdown = {
        "skills": points["skills"],
        "interests": points["interests"],
        "looking_for": points["looking_for"],
        "experience": _experience(me.get("experience_level"), other.get("experience_level")),
        "ai_agents": points["ai_agents"],
        "ide": WEIGHTS["ide"] if _same(me.get("favorite_ide"), other.get("favorite_ide")) else 0,
        "location": WEIGHTS["location"] if _same(me.get("location"), other.get("location")) else 0,
    }
    score = max(0, min(100, sum(breakdown.values())))
    label = next(name for floor, name in LABELS if score >= floor)
    return {
        "score": score,
        "label": label,
        "breakdown": breakdown,
        "max_breakdown": dict(WEIGHTS),
        "shared": shared,
    }


def rank_matches(me: dict[str, Any], others: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each profile in `others` with a `match` field added, most similar first."""
    matched = [{**other, "match": compute_match(me, other)} for other in others]
    # sorted() is stable, so ties keep the order they came in.
    return sorted(matched, key=lambda p: p["match"]["score"], reverse=True)


def _lower_set(values: list[str]) -> set[str]:
    return {value.lower() for value in values}


def _tech_stack(profile: dict[str, Any]) -> list[str]:
    """Skills plus every technology used in a project (shipping with it counts too)."""
    stack = list(profile["skills"])
    for project in profile["projects"]:
        stack.extend(project["technologies"])
    return stack


def _shared_points(shared: list[str], key: str, mine: list[str], theirs: list[str]) -> int:
    """An equal slice of WEIGHTS[key] per shared item, full points at FULL_AT[key] items
    (or at the longer list's length, when both lists are shorter than that)."""
    needed = min(FULL_AT[key], max(len(_lower_set(mine)), len(_lower_set(theirs))))
    if needed == 0:
        return 0  # neither of you listed anything, so there's nothing in common
    return round(min(1.0, len(shared) / needed) * WEIGHTS[key])


def _experience(a: str | None, b: str | None) -> int:
    """Full points for the same level, half for one step apart."""
    if a not in EXPERIENCE_ORDER or b not in EXPERIENCE_ORDER:
        return 0
    gap = abs(EXPERIENCE_ORDER.index(a) - EXPERIENCE_ORDER.index(b))
    return {0: WEIGHTS["experience"], 1: WEIGHTS["experience"] // 2}.get(gap, 0)


def _same(a: str | None, b: str | None) -> bool:
    a, b = (a or "").strip().lower(), (b or "").strip().lower()
    return bool(a) and a == b  # two blanks aren't "the same place"


def _shared(mine: list[str], theirs: list[str]) -> list[str]:
    mine_lower = _lower_set(mine)
    shared: list[str] = []
    for value in theirs:
        if value.lower() in mine_lower and value.lower() not in _lower_set(shared):
            shared.append(value)
    return shared
