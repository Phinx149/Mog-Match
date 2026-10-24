---
name: mog-score
description: Implement, tune, or debug the individual Mog Score, Team Mog Score, or recommendation ranking in C#. Use for anything touching MogMatch.Core/Scoring, MogMatch.Core/Matching, docs/MOG_SCORE.md, scoring weights, tiers, GitHub stats, or "why is my score X".
---

# Mog Score

Source of truth for the formula: `docs/MOG_SCORE.md`. Read it first. **If you change the formula, update the doc in the same PR.**

## Files
- `src/MogMatch.Core/Scoring/MogScoreCalculator.cs` — `MogResult Calculate(DeveloperProfile profile, GitHubStats? stats)`
- `src/MogMatch.Core/Scoring/TeamScoreCalculator.cs` — `TeamResult Calculate(IReadOnlyList<ScoredProfile> members)`
- `src/MogMatch.Core/Scoring/Weights.cs` — all maxes/weights as `const`s
- `src/MogMatch.Core/Scoring/MogTiers.cs` — score → tier name
- `src/MogMatch.Core/Matching/RecommendationRanker.cs`
- `src/MogMatch.Web/Services/GitHubStatsService.cs` — fetches + caches stats (24h)
- `tests/MogMatch.Core.Tests/Scoring/*Tests.cs`

## Rules
1. **Core stays pure.** Calculators take Core model objects (not EF entities) and return records. No `DbContext`, `HttpClient`, `DateTime.Now`, or `Random` inside. The Web project maps entities → Core models.
2. **One private method per component** (`CompletenessPoints`, `DepthPoints`, …), each `Math.Clamp`ed to its max; the total is clamped to `0..1000`.
3. **Return the breakdown + tips**, not just the number — the UI shows them.
4. **Deterministic.** The optional LLM bio rating is computed once, stored on the profile (`BioRating`), and passed in — the calculator never calls an API.
5. Static classes are fine for calculators (`public static class MogScoreCalculator`) — no state, easy to test.

## Skeleton
```csharp
namespace MogMatch.Core.Scoring;

public static class MogScoreCalculator
{
    public static MogResult Calculate(DeveloperProfile p, GitHubStats? stats)
    {
        var breakdown = new MogBreakdown(
            Completeness: CompletenessPoints(p),
            Depth:        DepthPoints(p.Skills),
            Breadth:      BreadthPoints(p.Skills),
            GitHub:       stats is null ? 0 : GitHubPoints(stats),
            Experience:   ExperiencePoints(p),
            Bio:          BioPoints(p));

        var score = Math.Clamp(breakdown.Total, 0, 1000);
        return new MogResult(score, MogTiers.For(score), breakdown, BuildTips(breakdown));
    }

    private static int DepthPoints(IReadOnlyList<Skill> skills)
    {
        var top5 = skills.OrderByDescending(s => s.Level).Take(5).Sum(s => s.Level * s.Level);
        return (int)Math.Round(top5 / 125.0 * Weights.DepthMax);
    }
    // ...other components
}
```

## Test first (xUnit)
```csharp
public class MogScoreCalculatorTests
{
    [Fact]
    public void EmptyProfile_ScoresNearZero_WithThreeTips()
    {
        var result = MogScoreCalculator.Calculate(TestProfiles.Empty, stats: null);
        Assert.True(result.Score < 50);
        Assert.Equal(3, result.Tips.Count);
    }

    [Fact]
    public void MaxedProfile_NeverExceeds1000()
    {
        var result = MogScoreCalculator.Calculate(TestProfiles.Maxed, TestProfiles.MaxedStats);
        Assert.Equal(1000, result.Score);
    }

    [Theory]
    [InlineData(0, "Hello World")]
    [InlineData(250, "Junior Mogger")]
    [InlineData(1000, "Gigamogger")]
    public void Tiers_MatchDoc(int score, string tier) => Assert.Contains(tier, MogTiers.For(score));
}
```
Put reusable fake profiles in `tests/MogMatch.Core.Tests/TestProfiles.cs`. Cover every item in the "Testing checklist" of `docs/MOG_SCORE.md`. Run `dotnet test`.

## GitHub stats
- `GET https://api.github.com/users/{username}` → `public_repos`, `followers`.
- `GET https://api.github.com/users/{username}/repos?per_page=100` → sum `stargazers_count`, collect `language`.
- Set a `User-Agent` header (GitHub rejects requests without one) and `Authorization: Bearer {GitHub:Token}` from configuration.
- Use a typed `HttpClient` (`AddHttpClient<GitHubStatsService>()`), deserialize with `System.Text.Json`.
- On failure, log and return `null` → GitHub component scores 0 instead of crashing.

## Debugging "why is my score X?"
Write a quick xUnit test that builds the user's profile values, calls `Calculate`, and inspects `result.Breakdown` against each component max in `docs/MOG_SCORE.md`.
