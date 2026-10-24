# CLAUDE.md

Context for Claude Code working in this repo.

## Project
MogMatch — a "dating"/matchmaking app for developers. Users build a tech profile, receive a **Mog Score** (0–1000), get recommended related/complementary devs, match, and chat (text + voice). Matched pairs/teams get a **Team Mog Score**. Hackathon project: favor working features over perfect architecture.

Read before big changes: `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/MOG_SCORE.md`.

## Stack
C# / .NET 10 · Blazor Web App (Interactive Server render mode) · ASP.NET Core Identity + GitHub OAuth · EF Core (SQLite dev, PostgreSQL prod) · SignalR (chat + WebRTC signaling) · WebRTC via JS interop (voice) · xUnit.

## Solution layout
- `src/MogMatch.Core` — domain models + scoring/matching logic. **No** EF, ASP.NET or HTTP dependencies.
- `src/MogMatch.Web` — Blazor app: components, `Data/` (DbContext, migrations), `Services/`, `Hubs/`, `wwwroot/js/`.
- `tests/MogMatch.Core.Tests` — xUnit tests for Core.

## Commands
- `dotnet watch --project src/MogMatch.Web` — run with hot reload
- `dotnet build` — must pass with no new warnings before merging
- `dotnet test`
- `dotnet format`
- `dotnet ef migrations add <Name> --project src/MogMatch.Web` / `dotnet ef database update --project src/MogMatch.Web`

## Conventions
- Logic in `MogMatch.Core` as pure, testable classes. `.razor` components stay thin and call injected services.
- Scoring code lives in `MogMatch.Core/Scoring/`; changes there need tests and must keep `docs/MOG_SCORE.md` in sync.
- Schema changes = new EF migration; never edit a migration already merged to `main`.
- Every query/hub method that touches user data checks the current user owns it or is a member of the match.
- Secrets via User Secrets (dev) / environment variables (prod); never in `appsettings.json`.
- Use `IDbContextFactory<AppDbContext>` in Blazor components (one short-lived context per operation), not a long-lived injected `DbContext`.
- Branch + PR workflow; conventional commits. See `CONTRIBUTING.md`.

## Team
Many contributors are beginner developers. When helping: explain *why*, keep changes small, prefer readable code over clever code.
