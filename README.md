# MogMatch 💘⚙️

> A "dating" app for developers. Build your tech profile, get your **Mog Score**, match with devs who complement you, and see how your team stacks up.

Built for the Social Coding Hackathon.

## The idea

1. **Tech Profile** – Users describe themselves: stack, languages, experience, projects, GitHub, what they want to build.
2. **Mog Score** – Every profile gets a 0–1000 score computed from the description and measurable metrics (repos, contributions, skill breadth/depth, profile completeness).
3. **Recommendations** – The app suggests developers with related or complementary profiles. Like/pass to match.
4. **Team Mog Score** – When two (or more) devs match, they get a combined team score that rewards *complementary* skills, not just high individual scores.
5. **Chat + Voice** – Matched users get a built-in real-time chat and can jump into a voice call.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language / runtime | **C# on .NET 10 (LTS)** | One language for UI, server and logic |
| UI | **Blazor Web App** (Interactive Server render mode) | Write UI in C# + Razor, no separate JS frontend |
| Styling | Bootstrap (ships with template) | Zero setup |
| Auth | ASP.NET Core Identity + GitHub OAuth | Built in; GitHub login gives us the username for stats |
| Database | EF Core — SQLite locally, PostgreSQL in prod | No DB install needed to start |
| Real-time chat | ASP.NET Core **SignalR** | Built into ASP.NET Core |
| Voice | Browser **WebRTC** via JS interop, signaling over SignalR | Peer-to-peer audio, no paid service |
| Scoring | Pure C# in `MogMatch.Core` | Fully unit-testable |
| Tests | xUnit | Default .NET test framework |

## Repo docs

| File | What's in it |
|---|---|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Setup, git workflow, code style — **start here** |
| [`CLAUDE.md`](CLAUDE.md) | Context for Claude Code / AI assistants |
| [`docs/PRODUCT.md`](docs/PRODUCT.md) | Features, user flows, screens, MVP scope |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, solution structure, data model |
| [`docs/MOG_SCORE.md`](docs/MOG_SCORE.md) | The individual + team scoring algorithm |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Hackathon task breakdown |
| [`.claude/skills/`](.claude/skills/) | Claude Code skills for common dev tasks |

## Quick start

```bash
git clone https://github.com/Phinx149/social-coding-Hackathon.git
cd social-coding-Hackathon
dotnet restore
dotnet ef database update --project src/MogMatch.Web
dotnet watch --project src/MogMatch.Web     # https://localhost:5001
```

> The solution isn't scaffolded yet — see `docs/ROADMAP.md` → Phase 0. In Claude Code, run the `/setup-project` skill to scaffold it.
