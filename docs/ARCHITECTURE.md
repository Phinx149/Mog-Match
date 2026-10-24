# Architecture

## Overview
```
 Browser
   │  Blazor Server circuit (SignalR connection, UI events)
   │  ChatHub (SignalR) — chat messages + WebRTC signaling
   │  WebRTC peer-to-peer audio  ◄──────────►  other user's browser
   ▼
 MogMatch.Web  (ASP.NET Core, .NET 10)
   ├─ Components/        Razor pages + components (Interactive Server)
   ├─ Hubs/ChatHub.cs    real-time chat + call signaling
   ├─ Services/          ProfileService, MatchService, GitHubStatsService, ...
   ├─ Data/              AppDbContext (EF Core) + Migrations
   └─ uses ─► MogMatch.Core  (scoring, team score, recommendation ranking)
   │
   ├──► SQLite (dev) / PostgreSQL (prod)
   └──► GitHub REST API (public repo / follower stats)
```

**Why Interactive Server?** All C# runs on the server, so components can call services and the DB directly — no separate API layer to build. Fine for hackathon-scale traffic.

## Solution structure
```
.
├── .claude/skills/                  # Claude Code skills
├── docs/
├── MogMatch.sln
├── src/
│   ├── MogMatch.Core/               # class library — NO web/EF dependencies
│   │   ├── Models/                  # DeveloperProfile, Skill, GitHubStats, Role, ...
│   │   ├── Scoring/                 # MogScoreCalculator, TeamScoreCalculator, MogTiers, Weights
│   │   └── Matching/                # RecommendationRanker, SkillSimilarity
│   └── MogMatch.Web/                # Blazor Web App
│       ├── Components/
│       │   ├── Layout/              # MainLayout, NavMenu
│       │   ├── Pages/               # Home, Onboarding, Discover, Matches, Chat, Profile
│       │   └── Shared/              # ProfileCard, MogBadge, ScoreBreakdown, ChatWindow, CallButton
│       ├── Data/
│       │   ├── AppDbContext.cs
│       │   ├── Entities/            # EF entity classes
│       │   └── Migrations/
│       ├── Hubs/ChatHub.cs
│       ├── Services/
│       ├── wwwroot/js/voice.js      # WebRTC helper called via IJSRuntime
│       ├── appsettings.json
│       └── Program.cs
└── tests/
    └── MogMatch.Core.Tests/         # xUnit
```

Dependency rule: `Web → Core`. `Core` never references `Web`. Tests reference `Core`.

## Data model (EF Core entities)

```csharp
public class AppUser : IdentityUser            // Identity table, 1:1 with Profile
{
    public Profile? Profile { get; set; }
}

public class Profile
{
    public Guid Id { get; set; }
    public string UserId { get; set; } = "";   // FK → AppUser
    public string DisplayName { get; set; } = "";
    public string? AvatarUrl { get; set; }
    public string? Headline { get; set; }       // ≤ 80
    public string? Bio { get; set; }            // ≤ 1000
    public List<string> Roles { get; set; } = [];       // "frontend", "ml", ...
    public List<string> LookingFor { get; set; } = [];
    public int YearsCoding { get; set; }
    public int Hackathons { get; set; }
    public string? GitHubUsername { get; set; }
    public string? LinkedInUrl { get; set; }
    public string? PortfolioUrl { get; set; }
    public string? GitHubStatsJson { get; set; }        // cached stats
    public DateTime? GitHubStatsFetchedAt { get; set; }
    public int? BioRating { get; set; }                 // optional LLM rating 0–10, cached
    public int MogScore { get; set; }
    public string? MogBreakdownJson { get; set; }
    public List<ProfileSkill> Skills { get; set; } = [];
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class ProfileSkill   { public Guid ProfileId; public string Name; public string Category; public int Level; } // PK (ProfileId, Name), Level 1–5
public class Swipe          { public Guid SwiperId; public Guid TargetId; public SwipeAction Action; public DateTime CreatedAt; } // PK (SwiperId, TargetId)
public enum  SwipeAction    { Pass, Like, Super }
public class Match          { public Guid Id; public Guid UserAId; public Guid UserBId; public int TeamScore; public string? TeamBreakdownJson; public DateTime CreatedAt; } // UserAId < UserBId, unique pair
public class Message        { public long Id; public Guid MatchId; public Guid SenderId; public string Body; public DateTime CreatedAt; } // Body ≤ 4000
public class Block          { public Guid BlockerId; public Guid BlockedId; }
```
(Shown compact; real files use properties and one class per file.)

`List<string>` columns are stored with EF Core primitive collections (JSON column) — works on both SQLite and PostgreSQL.

## Key flows

**Sign-in:** "Sign in with GitHub" → Identity external login → on first login create `Profile` with `GitHubUsername` + avatar → redirect to `/onboarding`.

**Score computation:** profile saved → `ProfileService.RecalculateScoreAsync` → `GitHubStatsService` (cached 24h) → `MogScoreCalculator.Calculate(profile, stats)` → save `MogScore` + `MogBreakdownJson`.

**Swipe / match:** `MatchService.SwipeAsync(me, target, action)` inside one DB transaction: insert `Swipe`; if action is Like/Super and the target already liked me → create `Match` with `TeamScoreCalculator.Calculate(...)`.

**Recommendations:** `MatchService.GetRecommendationsAsync(me)` → candidates = not me, not swiped, not blocked either way → `RecommendationRanker.Rank(me, candidates)` → top 20.

**Chat:** `ChatWindow` connects to `/hubs/chat`, calls `JoinMatch(matchId)` (hub verifies membership, adds to group `match-{id}`). `SendMessage` saves to DB then broadcasts `ReceiveMessage` to the group.

**Voice:** `CallButton` calls `voice.js` through `IJSRuntime`. The browsers exchange WebRTC offer/answer/ICE candidates via `ChatHub` methods (`SendSignal`), then audio flows peer-to-peer. Public STUN server (`stun:stun.l.google.com:19302`); TURN is a stretch goal.

## Authorization rules
- Pages except Home/Login have `@attribute [Authorize]`.
- Only the owner can edit a profile.
- Match, messages, hub groups and call signaling: only `UserA`/`UserB` of that match.
- Never trust IDs sent from the client — always resolve the current user from `AuthenticationStateProvider` / `Context.User` on the server.

## Configuration
| Key | Where | Notes |
|---|---|---|
| `ConnectionStrings:Default` | appsettings (dev SQLite) / env var (prod) | `Data Source=mogmatch.db` |
| `Authentication:GitHub:ClientId` / `ClientSecret` | User Secrets / env | GitHub OAuth app, callback `/signin-github` |
| `GitHub:Token` | User Secrets / env | raises GitHub API rate limit to 5000/h |
| `Anthropic:ApiKey` | User Secrets / env | optional, LLM bio rating |

In env vars use `__` for `:` (e.g. `Authentication__GitHub__ClientId`).
