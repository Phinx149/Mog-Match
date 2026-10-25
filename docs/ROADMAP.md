# Hackathon Roadmap

Three devs, 24 hours. Split work by **vertical feature** so each person ships end-to-end. Branch off `dev`, PR into `dev`, merge `dev` → `main` when demo-ready.

## Milestone 1 — Boilerplate ✅
- [x] Flask app factory, models, migrations, seed command
- [x] Profile API (list/filter, get, get/patch `me`) + pytest suite
- [x] React app: Discover (search, filters, like/pass), Profile, Edit Profile, Settings placeholder
- [x] README with setup + API docs

## Milestone 2 — Swipes & matches (next)
| Task | Notes |
|---|---|
| `swipes` + `matches` models & migration | see planned tables in `ARCHITECTURE.md` |
| `POST /api/swipes` | record like/pass for the demo user; create match on mutual like |
| `GET /api/matches` | list my matches |
| Discover excludes already-swiped profiles | server-side |
| Matches page + nav item | |
| Seed: a few seed profiles that already "liked" the demo user | so the demo produces a match instantly |

## Invites & inbox ✅
- [x] `invites` table + migration (sender, recipient, optional message, pending/accepted/declined)
- [x] Invite button on Match cards (only people you liked), Inbox page with Received/Sent, nav badge
- [x] Seed: three seeded profiles have already invited the demo user
- [x] Username + password login (seeded users, shared demo password) so two people can test invites
- [ ] Next: chat for accepted invites, ending in a generated project idea for the pair

## Milestone 3 — Intersect Engine (the differentiator)
- [ ] Compute overlap (shared skills/interests) and complement (skills only one has) for a pair
- [ ] Generate 2–3 project ideas for a match (LLM call, cached per match)
- [ ] "Intersect" panel on the match/profile page

## Milestone 4 — Stretch
- [x] Mog Score (see `MOG_SCORE.md`)
- [ ] Real-time chat for matches
- [ ] GitHub OAuth (replace demo user)
- [x] Deploy-ready: Postgres + Vercel config (`vercel.json`, `docs/DEPLOY.md`). Actual deploy: connect the repo in Vercel and follow the guide

## Demo prep (last 2 hours)
- [ ] Feature freeze — bug fixes only
- [ ] `flask seed --reset` before demo
- [ ] Rehearse: Discover → filter → like → match → Intersect ideas → profile edit
- [ ] README screenshots

## Team
| Name | GitHub | Focus |
|---|---|---|
| | | |
