# Mog Score

The Mog Score is a playful 0–100 rating of a developer profile. It must be **explainable** (every point comes from a visible component) and **gameable only by doing real things** (filling in your profile, shipping projects). The big twist: **the more esoteric your languages, the higher you score.**

Implementation: `backend/app/services/mog_score.py` (pure functions, no DB or HTTP calls), tests in `backend/tests/test_mog_score.py`. Every profile in the API carries a `mog` field. Keep this doc and the code in sync.

## Individual score (max 100)

| Component | Max | How it's computed |
|---|---|---|
| **Language esotericness** | 25 | Each language in your skills or project technologies earns points by rarity (below). **Full points only if it's used in a project**; listed only as a skill = half. Summed, rounded, capped at 25. |
| **Skill breadth** | 10 | 1 per skill, capped at 10 skills |
| **Links** | 6 | 2 per link, capped at 3 |
| **Projects** | 15 | 5 per project, capped at 3 |
| **Project descriptions** | 12 | Average description length, log-scaled; full points at 400 chars |
| **Profile completeness** | 15 | 1.5 each (rounded): avatar, location, education, favorite IDE, experience level, ≥ 1 AI agent, ≥ 2 interests, ≥ 1 looking-for, ≥ 3 skills, ≥ 1 project URL |
| **Experience** | 8 | Student 2 · Junior 4 · Mid-level 5 · Senior 7 · Lead 8 |
| **Bio** | 9 | Bio length, log-scaled; full points at 300 chars |

No GitHub stats for now: they need server-side fetching and caching. They can come later as a new component.

### Language rarity
| Tier | Points | Languages |
|---|---|---|
| Mainstream | 1 | Python, JavaScript, TypeScript, Java, HTML, CSS, SQL, C#, PHP, Bash, Shell, PowerShell |
| Common | 3 | Go, Rust, Kotlin, Swift, C, C++, Ruby, Dart, R, Scala, Sass, GraphQL, Lua, MATLAB, Objective-C, VB.NET, Groovy, Perl, HCL (and any catalog language not listed) |
| Niche | 7 | Haskell, Elixir, OCaml, Clojure, F#, Julia, Nim, Zig, Erlang, Elm, Racket, Crystal, Scheme, Solidity, GDScript, GLSL, HLSL, WebAssembly, Mojo, V, CoffeeScript |
| Arcane | 10 | COBOL, Fortran, Ada, Assembly, Prolog, Lisp, Verilog, VHDL, Pascal |

Only entries in `TECH_CATALOG["languages"]` count; frameworks, tools and specialties don't.

Log scaling (so 0 → 100 chars matters more than 300 → 400):
```python
def scaled(value, saturate_at, max_points):
    ratio = math.log10(1 + value) / math.log10(1 + saturate_at)
    return round(min(1.0, ratio) * max_points)
```

### Tiers
| Score | Tier | Roast |
|---|---|---|
| 0–24 | 🥚 Hello World | Just compiled their first print statement. Proud of them. |
| 25–44 | 🐣 Junior Mogger | Knows what a semicolon is. Mostly. |
| 45–64 | 🧑‍💻 Mid Mogger | Deploys on Fridays. It usually works. |
| 65–84 | 🔥 Senior Mogger | Their rubber duck asks them for advice. |
| 85–100 | 👑 Gigamogger | Writes Haskell for fun. Compilers apologize to them. |

### Result shape (API)
```json
{
  "score": 49,
  "tier": "Mid Mogger",
  "emoji": "🧑‍💻",
  "roast": "Deploys on Fridays. It usually works.",
  "breakdown": {"esoteric": 2, "breadth": 6, "links": 4, "projects": 5, "descriptions": 8, "completeness": 14, "experience": 2, "bio": 8},
  "max_breakdown": {"esoteric": 25, "breadth": 10, "links": 6, "projects": 15, "descriptions": 12, "completeness": 15, "experience": 8, "bio": 9},
  "tips": ["Ship a project in a language nobody's heard of. Haskell, Zig, COBOL: the weirder, the mog-ier. (+23)"]
}
```
`tips` = up to 3 (funny) suggestions for the components furthest from their max.

### Discover
`GET /api/profiles?min_tier=Mid%20Mogger` keeps profiles at or above a tier; `sort=mog` puts the highest scores first. The Discover page exposes both ("Anyone with a pulse" … "Gigamoggers (good luck)", "Biggest moggers first").

## Team Mog Score (max 1000) — not implemented yet

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
- Maxed profile → exactly 100, never above.
- Esoteric languages beat mainstream ones; a language used in a project beats one only listed.
- Two identical full-stack devs score lower as a team than a Frontend + Backend pair with the same individual scores.
- Same input → same output (no clock, randomness or I/O inside the scorer).
