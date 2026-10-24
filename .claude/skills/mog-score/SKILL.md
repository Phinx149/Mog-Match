---
name: mog-score
description: Implement, tune, or debug the Mog Score, Team Mog Score, or pair compatibility/Intersect calculations in MogMatch's Python backend. Use for anything touching docs/MOG_SCORE.md, backend/app/services/mog_score.py or intersect logic, scoring weights, tiers, or "why is my score X".
---

# Mog Score & pair scoring

The formula's source of truth is `docs/MOG_SCORE.md`. Read it first. **If you change the formula, update the doc in the same PR.** This is a later milestone. Check `docs/ROADMAP.md` before starting, and confirm with the user if earlier milestones are unfinished.

## Files (to create)
- `backend/app/services/mog_score.py`: `compute_mog_score(profile_data: dict, github_stats: dict | None) -> dict` and `compute_team_score(members: list[dict]) -> dict`
- `backend/tests/test_mog_score.py`
- API: `GET /api/profiles/<id>/score` or a `mog` field added in `profile_service.to_dict`

## Rules
1. **Pure functions.** Take plain dicts (e.g. `profile_service.to_dict(profile)`), return plain dicts. No DB queries, HTTP, `datetime.now()` or randomness inside, so tests are trivial and results are deterministic.
2. **One helper per component** (`_completeness`, `_breadth`, ...), each clamped to its max. Clamp the total to `0..1000`.
3. **Return `score`, `tier`, `breakdown`, `tips`.** The UI shows all four.
4. Put all weights in one `WEIGHTS` dict at the top so tuning is a one-line change.
5. Compare skills case-insensitively (`.lower()`), the same way `list_profiles` filtering does.
6. Expensive inputs (GitHub stats, LLM bio rating) are fetched elsewhere, cached on the profile, and passed in.

## Skeleton
```python
WEIGHTS = {"completeness": 150, "breadth": 200, "projects": 200, "github": 250, "experience": 100, "bio": 100}
TIERS = [(850, "Gigamogger"), (650, "Senior Mogger"), (450, "Mid Mogger"), (250, "Junior Mogger"), (0, "Hello World")]

def compute_mog_score(profile: dict, github_stats: dict | None = None) -> dict:
    breakdown = {
        "completeness": _completeness(profile),
        "breadth": min(len(profile["skills"]), 10) * 20,
        "projects": _projects(profile["projects"]),
        "github": _github(github_stats) if github_stats else 0,
        "experience": _experience(profile.get("experience_level")),
        "bio": _bio(profile),
    }
    score = max(0, min(1000, sum(breakdown.values())))
    tier = next(name for floor, name in TIERS if score >= floor)
    return {"score": score, "tier": tier, "breakdown": breakdown, "tips": _tips(breakdown)}
```

## Tests first
```python
from app.services.mog_score import compute_mog_score

def test_empty_profile_scores_low_with_tips():
    result = compute_mog_score(EMPTY_PROFILE)
    assert result["score"] < 50 and result["tier"] == "Hello World"
    assert len(result["tips"]) == 3

def test_score_never_exceeds_1000():
    assert compute_mog_score(MAXED_PROFILE, MAXED_STATS)["score"] == 1000
```
Cover every item in the "Testing checklist" in `docs/MOG_SCORE.md`. Run `pytest`.

## Debugging "why is my score X?"
Load the profile (`client.get("/api/profiles/me").get_json()` in a test, or the Flask shell), call `compute_mog_score`, and print `breakdown`. Compare each component against its max in `WEIGHTS`.
