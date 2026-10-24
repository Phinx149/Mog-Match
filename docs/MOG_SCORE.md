# Mog Score

The Mog Score is a playful 0–1000 rating of a developer profile. It must be **explainable** (every point comes from a visible component) and **gameable only by doing real things** (filling your profile, shipping code).

Implementation: `src/MogMatch.Core/Scoring/MogScoreCalculator.cs` and `TeamScoreCalculator.cs`. Tests: `tests/MogMatch.Core.Tests/Scoring/`. Keep this doc and the code in sync.

## Individual score (max 1000)

| Component | Max | How it's computed |
|---|---|---|
| **Profile completeness** | 100 | +10 per filled field (headline, bio ≥ 100 chars, avatar, ≥ 3 skills, roles, looking for, years, hackathons, ≥ 1 extra link, GitHub) |
| **Skill depth** | 200 | `sum(level²)` of top 5 skills ÷ 125 × 200 (five level-5 skills = max) |
| **Skill breadth** | 100 | distinct skill *categories* (language, framework, database, cloud, ML, design, …) × 20, capped |
| **GitHub activity** | 300 | log-scaled: public repos (80), stars received (80), contributions last year (100), followers (40) |
| **Experience** | 150 | years coding × 15 (cap 100) + hackathons × 10 (cap 50) |
| **Bio quality** | 150 | heuristic: length, mentions of concrete projects/tech that match listed skills. If an LLM rating (0–10) is cached on the profile, use `rating × 15` instead |

Log scaling for GitHub (so 1 → 100 repos matters more than 100 → 1000):
```csharp
static int Scaled(int value, int saturateAt, int max) =>
    (int)Math.Round(Math.Min(1.0, Math.Log10(1 + value) / Math.Log10(1 + saturateAt)) * max);

// repos:         Scaled(stats.PublicRepos,   50,   80)
// stars:         Scaled(stats.StarsReceived, 500,  80)
// contributions: Scaled(stats.Contributions, 1000, 100)
// followers:     Scaled(stats.Followers,     200,  40)
```

### Tiers
| Score | Tier |
|---|---|
| 0–249 | 🥚 Hello World |
| 250–449 | 🐣 Junior Mogger |
| 450–649 | 🧑‍💻 Mid Mogger |
| 650–849 | 🔥 Senior Mogger |
| 850–1000 | 👑 Gigamogger |

### Result types (`MogMatch.Core/Scoring`)
```csharp
public record MogBreakdown(int Completeness, int Depth, int Breadth, int GitHub, int Experience, int Bio)
{
    public int Total => Completeness + Depth + Breadth + GitHub + Experience + Bio;
}

public record MogResult(int Score, string Tier, MogBreakdown Breakdown, IReadOnlyList<string> Tips);
```
`Tips` = up to 3 suggestions for the components furthest from their max ("Add 2 more skills to gain up to +40").

## Team Mog Score (max 1000)

A great team isn't two clones. The team score rewards **complementarity** with enough **overlap** to communicate.

| Component | Max | How |
|---|---|---|
| **Combined strength** | 400 | average of members' individual scores × 0.4 |
| **Role coverage** | 250 | distinct roles across the team; frontend + backend + (design or ML or devops) = full marks |
| **Skill complementarity** | 200 | Jaccard *distance* of skill sets, peaks around 0.65 |
| **Shared ground** | 100 | ≥ 1 shared language/framework = 60, shared "looking for" = 40 |
| **Experience balance** | 50 | penalty if one has 0 hackathons and the other 10+ (unless "looking for" includes mentor/mentee) |

```csharp
var union        = a.Skills.Select(s => s.Name).Union(b.Skills.Select(s => s.Name)).Count();
var intersection = a.Skills.Select(s => s.Name).Intersect(b.Skills.Select(s => s.Name)).Count();
double distance  = union == 0 ? 0 : 1 - (double)intersection / union;           // 0..1
int complementarity = (int)Math.Round(200 * Math.Max(0, 1 - Math.Abs(distance - 0.65) / 0.65));
```

### Recommendation ranking (`MogMatch.Core/Matching/RecommendationRanker.cs`)
```
recommendScore = 0.6 × predictedTeamScore / 1000 + 0.4 × similarity
similarity     = cosine similarity of skill vectors (skill name → level)
```
Exclude: self, already swiped, blocked in either direction (done in the query, before ranking).

## Testing checklist (xUnit)
- Empty profile → score < 50, tier Hello World, 3 tips.
- Maxed profile → exactly 1000, never above.
- `githubStats == null` → GitHub component is 0, no exception.
- Two identical fullstack devs score lower as a team than a frontend + backend pair with the same individual scores.
- Same input → same output (no `DateTime.Now`, randomness or I/O in the calculators).
