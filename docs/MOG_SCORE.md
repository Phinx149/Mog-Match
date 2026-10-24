# Mog Score (stretch milestone — not implemented yet)

The Mog Score is a playful 0–1000 rating of a developer profile. It must be **explainable** (every point comes from a visible component) and **gameable only by doing real things** (filling in your profile, shipping projects).

Planned implementation: `backend/app/services/mog_score.py` (pure functions, no DB or HTTP calls) with tests in `backend/tests/test_mog_score.py`. Keep this doc and the code in sync.

## Individual score (max 1000)

Based on the fields the `profiles` table already has:

| Component | Max | How it's computed |
|---|---|---|
| **Profile completeness** | 150 | 15 points each: avatar, location, education, bio ≥ 100 chars, ≥ 3 skills, ≥ 2 interests, favorite IDE, ≥ 1 AI agent, ≥ 1 link, experience level |
| **Skill breadth** | 200 | 20 per skill, capped at 10 skills |
| **Projects** | 200 | 60 per project (cap 3) + 20 if ≥ 1 has a URL; technologies that match listed skills add credibility, not points |
| **GitHub activity** | 250 | log-scaled public repos (80), stars (80), followers (40), recent activity (50). Needs a GitHub link; fetched server-side and cached |
| **Experience** | 100 | Student 20 · Junior 40 · Mid-level 60 · Senior 80 · Lead 100 |
| **Bio quality** | 100 | length + mentions of listed skills/projects. Optionally an LLM rating 0–10 × 10, cached on the profile |

Log scaling (so 1 → 100 repos matters more than 100 → 1000):
```python
import math

def scaled(value: int, saturate_at: int, max_points: int) -> int:
    ratio = math.log10(1 + value) / math.log10(1 + saturate_at)
    return round(min(1.0, ratio) * max_points)

# repos: scaled(repos, 50, 80)   stars: scaled(stars, 500, 80)   followers: scaled(followers, 200, 40)
```

### Tiers
| Score | Tier |
|---|---|
| 0–249 | 🥚 Hello World |
| 250–449 | 🐣 Junior Mogger |
| 450–649 | 🧑‍💻 Mid Mogger |
| 650–849 | 🔥 Senior Mogger |
| 850–1000 | 👑 Gigamogger |

### Result shape (API)
```json
{
  "score": 612,
  "tier": "Mid Mogger",
  "breakdown": {"completeness": 135, "breadth": 120, "projects": 140, "github": 97, "experience": 60, "bio": 60},
  "tips": ["Add a project URL for +20", "Add 2 more skills for up to +40"]
}
```
`tips` = up to 3 suggestions for the components furthest from their max.

## Team Mog Score (max 1000)

A great team isn't two clones. The team score rewards **complementarity** with enough **overlap** to communicate — the same idea the Intersect Engine uses.

| Component | Max | How |
|---|---|---|
| **Combined strength** | 400 | average of members' scores × 0.4 |
| **Specialty coverage** | 250 | distinct specialty tags across the team (Frontend, Backend, Machine Learning, DevOps, Mobile, …) |
| **Skill complementarity** | 200 | Jaccard *distance* of skill sets, peaks around 0.65 |
| **Shared ground** | 100 | ≥ 1 shared skill = 60, shared `looking_for` = 40 |
| **Experience balance** | 50 | penalty for Student + Lead unless one is looking for Mentor and the other for Mentee |

```python
def complementarity(a_skills: list[str], b_skills: list[str]) -> int:
    a, b = {s.lower() for s in a_skills}, {s.lower() for s in b_skills}
    union = a | b
    distance = 0.0 if not union else 1 - len(a & b) / len(union)   # 0..1
    return round(200 * max(0.0, 1 - abs(distance - 0.65) / 0.65))
```

## Testing checklist (pytest)
- Empty profile → score < 50, tier Hello World, 3 tips.
- Maxed profile → exactly 1000, never above.
- No GitHub stats → GitHub component is 0, no exception.
- Two identical full-stack devs score lower as a team than a Frontend + Backend pair with the same individual scores.
- Same input → same output (no clock, randomness or I/O inside the scorer).
