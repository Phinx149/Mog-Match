# Mog Match

When you **like** someone on Discover they become one of your matches, scored 0–100 by **how similar their profile is to yours**. Passes are saved too but never become matches. Likes live in the `swipes` table (`backend/app/models/swipe.py`, logic in `backend/app/services/swipe_service.py`). The Mog Score rates one profile on its own; Mog Match compares two.

Implementation: `backend/app/services/mog_match.py` (pure functions, no DB or HTTP calls), tests in `backend/tests/test_mog_match.py`. Keep this doc and the code in sync.

## Score (max 100)

| Component | Max | How it's computed |
|---|---|---|
| **Tech stack** | 45 | Shared skills + project technologies; full at **5** shared (9 each) |
| **Interests** | 24 | Shared interests; full at **3** shared (8 each) |
| **Goals** | 10 | Shared `looking_for`; full at **2** shared. The same goal matches, and **Mentor ↔ Mentee also count as a match** |
| **Experience** | 10 | Same level = 10, one step apart = 5, otherwise 0 |
| **AI agents** | 5 | Shared favorite AI agents; full at 2 shared |
| **IDE** | 3 | Same favorite IDE |
| **Location** | 3 | Same location (exact text, ignoring case) |

Comparisons ignore case. We **count shared items** instead of dividing by the combined list size (Jaccard): with Jaccard, a long skill list watered down real overlap, so tech barely mattered and the few, widely shared goals decided the ranking. Goals are low-weight for the same reason: there are only 7 options, so almost everyone shares one.

```python
needed = min(FULL_AT[key], max(len(mine), len(theirs)))
points = round(min(1.0, len(shared) / needed) * WEIGHTS[key])
```

If both lists are shorter than `FULL_AT`, sharing the whole longer list is enough. **Guarantee: an exact copy of a profile scores 100** (tested for every seeded profile). The one exception is a field that's empty on both sides: nothing listed means nothing in common, so it scores 0.

### Labels
| Score | Label |
|---|---|
| 80–100 | Basically your twin |
| 60–79 | Same wavelength |
| 40–59 | Solid common ground |
| 20–39 | A few things in common |
| 0–19 | Total strangers |

## API
- `POST /api/swipes` `{"target_id": "<uuid>", "action": "like" | "pass"}` → `201 {"target_id", "action", "match"}` (`match` is the score below for a like, `null` for a pass). Swiping on the same person again overwrites. `400` for bad input or swiping on yourself, `404` for an unknown profile.
- `DELETE /api/swipes` → `{"removed": n}`: forget all my likes/passes (Discover's "Start over").
- `GET /api/profiles/me/matches` → `{"matches": [...], "count": n}`: everyone I liked, most similar first. Each entry is a full profile plus:

```json
"match": {
  "score": 41,
  "label": "Solid common ground",
  "breakdown": {"skills": 18, "interests": 8, "looking_for": 5, "experience": 5, "ai_agents": 5, "ide": 0, "location": 0},
  "max_breakdown": {"skills": 45, "interests": 24, "looking_for": 10, "experience": 10, "ai_agents": 5, "ide": 3, "location": 3},
  "shared": {"skills": ["Full-stack", "React"], "interests": ["Startups"], "looking_for": ["Side project"], "ai_agents": ["GitHub Copilot", "Claude Code"]}
}
```

Discover (`GET /api/profiles`) hides anyone I've already liked or passed. The frontend shows matches on the **Match** page (`/match`), and Discover shows the score right after a like.

## Not yet
Similarity ≠ a good team. Complementary skills (the Team Mog Score and Intersect Engine in `MOG_SCORE.md` / `ROADMAP.md`) are a separate, later feature.
