# Hackathon Roadmap

Split work by **vertical feature**, not by layer, so each person can ship something end-to-end. Tick boxes in PRs.

## Phase 0 — Setup (everyone, first hour)
- [ ] Scaffold the solution (`/setup-project` skill) and push to `main`
- [ ] Create a GitHub OAuth app (callback `https://localhost:5001/signin-github`), share ID/secret privately
- [ ] Everyone installs the .NET 10 SDK, clones, runs `dotnet watch`, and makes a test PR (add your name to the Team table below)

## Phase 1 — MVP
| Track | Tasks | Skill to use |
|---|---|---|
| **Auth + Profile** | GitHub login, onboarding form (`EditForm`), profile page, skills editor | `/new-feature`, `/db-migration` |
| **Mog Score** | `MogScoreCalculator` + xUnit tests, `GitHubStatsService`, breakdown UI + `MogBadge` | `/mog-score` |
| **Discover + Match** | Swipe/Match entities, `MatchService`, `RecommendationRanker`, discover card UI | `/db-migration`, `/mog-score` |
| **Chat** | Message entity, `ChatHub`, `ChatWindow`, matches list page | `/realtime-chat` |

## Phase 2 — Polish & stretch
- [ ] Team Mog Score on matches + chat header
- [ ] Voice chat (`/voice-chat`)
- [ ] Mog Score reveal animation 🎉
- [ ] Leaderboard
- [ ] Deploy (Azure App Service free tier, or a container on Railway/Fly.io)

## Phase 3 — Demo (last 2 hours)
- [ ] Seed 15–20 fake profiles (`DbSeeder` on startup in Development)
- [ ] Freeze features — bug fixes only
- [ ] Rehearse demo: sign up → score reveal → swipe → match → chat → call
- [ ] Slides / README screenshots

## Team
| Name | GitHub | Track |
|---|---|---|
| | | |
