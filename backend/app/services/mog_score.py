"""Mog Score: a playful 0-100 rating of a developer profile. See docs/MOG_SCORE.md.

Pure functions only: they take the dict from `profile_service.to_dict` (minus "mog") and
return plain dicts. No DB, HTTP, clock or randomness, so the same profile always gets the
same score.
"""

import math
from typing import Any

from .tech_catalog import TECH_CATALOG

# Max points per component. They add up to 100; tune here.
WEIGHTS: dict[str, int] = {
    "esoteric": 25,
    "breadth": 10,
    "links": 6,
    "projects": 15,
    "descriptions": 12,
    "completeness": 15,
    "experience": 8,
    "bio": 9,
}

# Points per language by how obscure it is. A language only counts in full when it shows
# up in one of your projects; just listing it as a skill earns half (anyone can type "COBOL").
RARITY_POINTS = {"mainstream": 1, "common": 3, "niche": 7, "arcane": 10}
LANGUAGE_RARITY: dict[str, str] = {
    **dict.fromkeys(
        ["Python", "JavaScript", "TypeScript", "Java", "HTML", "CSS", "SQL", "C#", "PHP",
         "Bash", "Shell", "PowerShell"],
        "mainstream",
    ),
    **dict.fromkeys(
        ["Go", "Rust", "Kotlin", "Swift", "C", "C++", "Ruby", "Dart", "R", "Scala", "Sass",
         "GraphQL", "Lua", "MATLAB", "Objective-C", "VB.NET", "Groovy", "Perl", "HCL"],
        "common",
    ),
    **dict.fromkeys(
        ["Haskell", "Elixir", "OCaml", "Clojure", "F#", "Julia", "Nim", "Zig", "Erlang",
         "Elm", "Racket", "Crystal", "Scheme", "Solidity", "GDScript", "GLSL", "HLSL",
         "WebAssembly", "Mojo", "V", "CoffeeScript"],
        "niche",
    ),
    **dict.fromkeys(
        ["COBOL", "Fortran", "Ada", "Assembly", "Prolog", "Lisp", "Verilog", "VHDL", "Pascal"],
        "arcane",
    ),
}
# Lowercase name -> rarity, for every language in the catalog (unlisted ones count as common).
_RARITY_BY_KEY: dict[str, str] = {
    language.lower(): LANGUAGE_RARITY.get(language, "common") for language in TECH_CATALOG["languages"]
}

EXPERIENCE_POINTS = {"Student": 2, "Junior": 4, "Mid-level": 5, "Senior": 7, "Lead": 8}

# (min score, tier, emoji, roast), highest first.
TIERS = [
    (85, "Gigamogger", "👑", "Writes Haskell for fun. Compilers apologize to them."),
    (65, "Senior Mogger", "🔥", "Their rubber duck asks them for advice."),
    (45, "Mid Mogger", "🧑‍💻", "Deploys on Fridays. It usually works."),
    (25, "Junior Mogger", "🐣", "Knows what a semicolon is. Mostly."),
    (0, "Hello World", "🥚", "Just compiled their first print statement. Proud of them."),
]
TIER_NAMES = [name for _, name, _, _ in TIERS]

TIPS = {
    "esoteric": "Ship a project in a language nobody's heard of. Haskell, Zig, COBOL: the weirder, the mog-ier.",
    "breadth": "List more skills. Recruiters can't stalk what you don't list.",
    "links": "Add your links. A dev without a GitHub link is just a rumor.",
    "projects": "Add projects. \"Trust me, I've built stuff\" is not a portfolio.",
    "descriptions": "Write longer project descriptions. \"it does stuff\" is not a README.",
    "completeness": "Finish your profile. Even your IDE wants a shout-out.",
    "experience": "Level up your experience. Imposter syndrome is not an option in the dropdown.",
    "bio": "Write a real bio. \"I code\" is a hostage note, not a bio.",
}


def scaled(value: float, saturate_at: float, max_points: int) -> int:
    """Log-scale `value` so early gains matter most; full points at `saturate_at`."""
    ratio = math.log10(1 + max(0, value)) / math.log10(1 + saturate_at)
    return round(min(1.0, ratio) * max_points)


def compute_mog_score(profile: dict[str, Any]) -> dict[str, Any]:
    breakdown = {
        "esoteric": _esoteric(profile),
        "breadth": min(len(profile["skills"]), 10),
        "links": min(len(profile["links"]), 3) * 2,
        "projects": min(len(profile["projects"]), 3) * 5,
        "descriptions": _descriptions(profile["projects"]),
        "completeness": _completeness(profile),
        "experience": EXPERIENCE_POINTS.get(profile.get("experience_level") or "", 0),
        "bio": scaled(len(profile.get("bio") or ""), 300, WEIGHTS["bio"]),
    }
    breakdown = {key: max(0, min(WEIGHTS[key], value)) for key, value in breakdown.items()}
    score = max(0, min(100, sum(breakdown.values())))
    _, tier, emoji, roast = next(t for t in TIERS if score >= t[0])
    return {
        "score": score,
        "tier": tier,
        "emoji": emoji,
        "roast": roast,
        "breakdown": breakdown,
        "max_breakdown": dict(WEIGHTS),
        "tips": _tips(breakdown),
    }


def tier_floor(tier: str) -> int | None:
    """Minimum score for a tier name (case-insensitive), or None if it isn't a tier."""
    return next((floor for floor, name, _, _ in TIERS if name.lower() == tier.lower()), None)


def _esoteric(profile: dict[str, Any]) -> int:
    used = {tech.lower() for project in profile["projects"] for tech in project["technologies"]}
    listed = {skill.lower() for skill in profile["skills"]}
    points = 0.0
    for language in used | listed:
        rarity = _RARITY_BY_KEY.get(language)
        if rarity is None:
            continue  # frameworks, tools and specialties aren't languages
        full = RARITY_POINTS[rarity]
        points += full if language in used else full / 2
    return round(points)


def _descriptions(projects: list[dict]) -> int:
    if not projects:
        return 0
    average = sum(len(project["description"] or "") for project in projects) / len(projects)
    return scaled(average, 400, WEIGHTS["descriptions"])


def _completeness(profile: dict[str, Any]) -> int:
    checks = [
        profile.get("avatar_url"),
        profile.get("location"),
        profile.get("education"),
        profile.get("favorite_ide"),
        profile.get("experience_level"),
        len(profile["favorite_ai_agents"]) >= 1,
        len(profile["interests"]) >= 2,
        len(profile["looking_for"]) >= 1,
        len(profile["skills"]) >= 3,
        any(project.get("project_url") for project in profile["projects"]),
    ]
    return round(WEIGHTS["completeness"] * sum(1 for check in checks if check) / len(checks))


def _tips(breakdown: dict[str, int]) -> list[str]:
    """Up to 3 tips for the components furthest from their max (ties keep WEIGHTS order)."""
    gaps = sorted(WEIGHTS, key=lambda key: WEIGHTS[key] - breakdown[key], reverse=True)
    return [f"{TIPS[key]} (+{WEIGHTS[key] - breakdown[key]})" for key in gaps[:3] if breakdown[key] < WEIGHTS[key]]
