# MogMatch 💜

> A developer matchmaking platform. Build a technical profile, discover other developers, filter by skills and interests — and (soon) match with people whose skills *intersect* with yours.

Built for the Social Coding Hackathon — theme **Connect & Intersect**. Our headline feature (coming in a later milestone) is the **Intersect Engine**: it looks at two developers' complementary skills and shared interests and recommends projects they could build together.

## Current milestone

✅ Profiles stored in SQLite · ✅ Profile page · ✅ Edit profile with photo upload · ✅ Discover page with search + filters · ✅ Like/Pass (saved) · ✅ Mog Score · ✅ Mog Match (everyone you liked, ranked by similarity) · ✅ Invites + Inbox · ✅ Username + password login

⏳ Later: chat for accepted invites, Intersect Engine, Team Mog Score, sign-up, voice, GitHub login.

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 19 + Vite + TypeScript, Tailwind CSS v4, React Router, Lucide icons |
| Backend | Python 3.12+, Flask, Flask-CORS, Flask-SQLAlchemy, Flask-Migrate, python-dotenv |
| Database | SQLite (dev) via SQLAlchemy ORM — portable UUID/JSON columns, so PostgreSQL is a `DATABASE_URL` change |
| Tests | pytest (backend), `tsc` type checking (frontend) |

## Repository structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask application factory + JSON error handlers
│   │   ├── config.py            # env-driven config (DATABASE_URL, CORS_ORIGINS, SECRET_KEY, SEED_PASSWORD...)
│   │   ├── extensions.py        # db, migrate (+ SQLite foreign keys on)
│   │   ├── models/              # User, Profile, ProfileLink, Project, Swipe, Invite
│   │   ├── routes/              # health, auth, profiles, swipes, invites (thin: parse → service → JSON)
│   │   ├── services/            # the logic: auth, profile, swipe, invite, mog_score, mog_match, tech_catalog
│   │   └── seed.py              # `flask seed` / `flask seed-test-users` commands + sample data
│   ├── migrations/              # Alembic migrations (Flask-Migrate)
│   ├── tests/                   # pytest
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/          # layout/, profiles/, discover/, match/, invites/, mog/, forms/, common/
│   │   ├── pages/               # Login, Discover, Match, Inbox, Profile, EditProfile, Settings, NotFound
│   │   ├── services/api.ts      # typed fetch wrapper for the Flask API (sends the login cookie)
│   │   ├── types/               # profile.ts, invite.ts, auth.ts — match the API's JSON
│   │   ├── hooks/               # useAuth.tsx (who is logged in), useDebouncedValue
│   │   ├── App.tsx              # routes
│   │   └── main.tsx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.ts
├── docs/                        # product, architecture, roadmap, scoring notes
├── .claude/skills/              # Claude Code skills for common dev tasks
├── CLAUDE.md
└── CONTRIBUTING.md
```

## Prerequisites

- **Python 3.12+** — `python --version` (Windows: `py -3.12 --version` or newer)
- **Node.js 20.19+ or 22+** and npm — `node -v`
- **Git**

## Backend setup

From the `backend/` folder:

**macOS / Linux / WSL**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade        # create tables
flask seed              # demo user + 10 developers, all with the demo password
flask seed-test-users   # optional: quick-login accounts user1 / user2
python run.py           # http://localhost:5001
```

**Windows (PowerShell)**
```powershell
cd backend
py -3 -m venv .venv
.venv\Scripts\Activate.ps1      # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
Copy-Item .env.example .env
flask db upgrade
flask seed
flask seed-test-users   # optional: quick-login accounts user1 / user2
python run.py
```

> `flask` commands find the app through `FLASK_APP=run.py` in `.env`. Run them from `backend/` with the venv active.

## After you `git pull`

Someone may have added a table, column or package. From `backend/` with the venv active:
```bash
pip install -r requirements.txt   # new Python packages
flask db upgrade                  # new tables/columns (e.g. invites, users.password_hash)
flask seed                        # fills in anything missing (e.g. passwords for seeded users); never overwrites edits
```
and from `frontend/`: `npm install`. Then restart `python run.py` and `npm run dev`.

## Frontend setup

From the `frontend/` folder (any OS):
```bash
cd frontend
npm install
cp .env.example .env.local      # Windows PowerShell: Copy-Item .env.example .env.local
npm run dev                     # http://localhost:5173
```

## Environment variables

**`backend/.env`**
| Variable | Default | Purpose |
|---|---|---|
| `FLASK_APP` | `run.py` | Lets `flask db` / `flask seed` find the app |
| `DATABASE_URL` | *(empty → `backend/instance/mogmatch.db`)* | SQLAlchemy URL, e.g. `postgresql://user:pass@host/db` |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Origins allowed to call `/api/*` |
| `DEMO_USER_EMAIL` | `demo@mogmatch.dev` | The seeded demo user (username `jordan-dev`) |
| `SECRET_KEY` | `dev-only-not-secret` | Signs the login cookie. Set a long random value anywhere but your laptop |
| `SEED_PASSWORD` | see `.env.example` | Password `flask seed` gives every seeded user |
| `PORT` | `5001` | Port for `python run.py` (5000 clashes with AirPlay on macOS) |

**`frontend/.env.local`**
| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `http://localhost:5001` | Flask API base URL |

Never commit `.env`, `.env.local` or `*.db` files — they're git-ignored.

## Database migrations

Run from `backend/` with the venv active:
```bash
flask db upgrade                         # apply all migrations
flask db migrate -m "add something"      # after changing models: generate a migration
                                         # → review the file in migrations/versions/ before committing
flask db downgrade                       # undo the last migration
```

## Seed data

```bash
flask seed           # idempotent: creates missing seed profiles, never overwrites edited ones
flask seed --reset   # restores the demo user and all seeded profiles to their defaults
flask seed-test-users # quick-login accounts user1 / user2 that already like each other (passwords in TEST_USERS, app/seed.py); add --reset for a clean start
```
Seeds one **demo user** (Jordan Avery, `jordan-dev`) plus 10 developers across frontend, backend, full-stack, AI/ML, game dev, cybersecurity, data engineering, mobile and DevOps. Every seeded account gets the `SEED_PASSWORD` password, and three of them (Priya, Lena, Noah) have already sent Jordan an invite.

## Running locally

Two terminals:
1. `backend/` → activate venv → `python run.py`
2. `frontend/` → `npm run dev`

Open http://localhost:5173 (use `localhost`, not `127.0.0.1`, or the login cookie won't reach the API). The green **ping** pill in the top bar confirms the frontend can reach the API.

## Logging in

Every page except `/login` needs a login. There is no sign-up yet; use a seeded account:

| Username | Password | Notes |
|---|---|---|
| `jordan-dev` | `SEED_PASSWORD` from `backend/.env.example` | The demo user. Three seeded invites are waiting in their inbox |
| `samfullstack`, `priya-ml`, `mayacodes`, … (all 10 seeded devs) | same `SEED_PASSWORD` | |
| `user1`, `user2` | see `TEST_USERS` in `backend/app/seed.py` | Only after `flask seed-test-users`. They already like each other |

**Testing two people at once** (e.g. invites): log in as one user in a normal window and the other in an **incognito/private window**. Normal tabs share one login cookie, so logging in in a second tab switches *every* tab to that user (tabs notice and reload when you click back into them). Check the `@username` at the top right.

**Clean start for a demo or a test:** `flask seed --reset && flask seed-test-users --reset` — restores every seeded account and deletes their likes and invites. Everyone gets logged out (the users are recreated).

**Login trouble?**
| Symptom | Fix |
|---|---|
| "Wrong username or password" for a seeded user after pulling | `flask seed` (gives seeded users their password) — or `SEED_PASSWORD` in your `.env` differs from `.env.example` |
| `no such column: users.password_hash` / `no such table: invites` | `flask db upgrade` |
| Logged in, but every page bounces back to `/login` | You opened `127.0.0.1:5173`; use `http://localhost:5173` |
| Suddenly logged out | Someone ran `flask seed --reset` (it recreates users). Log in again |
| Two tabs show the same person | Expected: normal tabs share one login. Use an incognito window for the second user |

## Flask command cheat sheet

Run from `backend/` with the venv active (Windows without activating: `.venv\Scriptslask ...`).

| Command | What it does |
|---|---|
| `python run.py` | Start the API on :5001 (auto-reloads on code changes) |
| `flask db upgrade` | Apply all migrations (do this after every pull) |
| `flask db migrate -m "msg"` | After changing a model: generate a migration, then **read** it in `migrations/versions/` |
| `flask db downgrade` | Undo the last migration |
| `flask db check` | Fails if models and migrations are out of sync |
| `flask seed` | Add missing seed data (profiles, passwords, invites). Safe to run any time |
| `flask seed --reset` | Restore all seeded accounts to their defaults (deletes their likes/invites) |
| `flask seed-test-users [--reset]` | Add (or recreate) `user1` / `user2` for quick two-person testing. Local only |
| `pytest` | Backend tests |

## Tests & checks

```bash
# backend (from backend/, venv active)
pytest

# frontend (from frontend/)
npm run typecheck
npm run build
```

## API

All responses are JSON. Errors look like `{"error": {"message": "...", "fields": {"field": "problem"}}}`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | `{"status": "ok", "database": "ok"}` |
| GET | `/api/profiles` | Discoverable profiles (excludes me and people I swiped on) → `{"profiles": [...], "count": n}` |
| GET | `/api/profiles/filter-options` | Every allowed value for the list fields → `{"skills": [...], "looking_for": [...]}`. Powers the Discover filter menu and the Edit Profile "Looking for" picker |
| GET | `/api/profiles/<uuid>` | One profile, `404` if missing |
| POST | `/api/auth/login` | `{"username", "password"}` → `{"user": {...}}` and a session cookie. `401` for a wrong username or password |
| POST | `/api/auth/logout` | Ends the session → `{"user": null}` |
| GET | `/api/auth/session` | Who am I → `{"user": {...}}`, or `{"user": null}` when logged out |
| GET | `/api/profiles/me` | My profile (`401` when logged out, same for every `/me`, swipe and invite endpoint) |
| PATCH | `/api/profiles/me` | Partial update of my profile |
| GET | `/api/profiles/me/matches` | Mog Match: everyone I liked, most similar first, each with a `match` score. See `docs/MOG_MATCH.md` |
| POST | `/api/swipes` | Like or pass: `{"target_id", "action": "like" \| "pass"}` → `201` with the match score for a like. Swiped profiles leave Discover |
| DELETE | `/api/swipes/<uuid>` | Unlike one person: removes them from my matches and returns them to Discover (`404` if never swiped) |
| DELETE | `/api/swipes` | Forget all my likes/passes → `{"removed": n}` |
| POST | `/api/invites` | Invite someone I liked: `{"recipient_id", "message"?}` (message ≤ 280 chars) → `201` invite. `400` if I haven't liked them, `409` if either of us already invited the other |
| GET | `/api/invites/inbox` | `{"received": [...], "sent": [...], "pending_count": n}`, newest first |
| PATCH | `/api/invites/<uuid>` | Answer an invite sent to me: `{"status": "accepted" \| "declined"}`. `404` if it isn't mine, `409` if already answered |
| DELETE | `/api/invites/<uuid>` | Cancel an invite I sent while it's still pending |

**`GET /api/profiles` query params** (all optional, case-insensitive):
| Param | Example | Behavior |
|---|---|---|
| `q` | `q=rust` | Text search over name, username, bio, location, education, IDE, skills, interests, AI agents, project titles |
| `skills` | `skills=Rust,Frontend` or repeated | Profile must have **all** listed skills |
| `interests` | `interests=AI` | Profile must have **all** listed interests |
| `looking_for` | `looking_for=Mentor,Mentee` | Profile must be looking for **any** listed option |
| `location` | `location=berlin` | Substring match |
| `min_tier` | `min_tier=Mid Mogger` | Only profiles at or above this Mog tier (`400` if unknown) |
| `sort` | `sort=mog` | Highest Mog Score first |

Every profile includes a read-only `mog` object (`score`, `tier`, `emoji`, `roast`, `breakdown`, `max_breakdown`, `tips`). See `docs/MOG_SCORE.md`.

**Profile shape**
```json
{
  "id": "uuid", "user_id": "uuid",
  "full_name": "Maya Chen", "username": "mayacodes", "avatar_url": null,
  "location": "San Francisco, CA", "education": "B.A. Cognitive Science, UC Berkeley",
  "bio": "...", "favorite_ide": "VS Code", "favorite_ai_agents": ["Cursor", "Claude Code"],
  "skills": ["Frontend", "TypeScript", "React"], "interests": ["Design Systems"],
  "experience_level": "Senior", "looking_for": ["Side project"],
  "links": [{"id": "uuid", "label": "GitHub", "url": "https://..."}],
  "projects": [{"id": "uuid", "title": "Prism UI", "description": "...", "project_url": "https://...", "technologies": ["React"]}],
  "created_at": "ISO-8601", "updated_at": "ISO-8601"
}
```

**`PATCH /api/profiles/me`** accepts any subset of: `full_name`, `username`, `avatar_url`, `location`, `education`, `bio`, `favorite_ide`, `experience_level` (`Student | Junior | Mid-level | Senior | Lead`), `skills`, `interests`, `favorite_ai_agents`, `looking_for` (fixed list, see below), `links` (`[{label, url}]`), `projects` (`[{title, description, project_url, technologies}]`).
- `links` and `projects`, when sent, **replace** the existing lists.
- Tags are trimmed and de-duplicated (case-insensitive). URLs must be `http(s)`.
- `skills` must come from the tech catalog and `looking_for` from `Hackathon team | Side project | Open source | Cofounder | Mentor | Mentee | Just vibes` (case-insensitive; stored with the canonical spelling). `GET /api/profiles/filter-options` returns both lists.
- `400` on invalid data or unknown fields, `409` if the username is taken.

## Known limitations (this milestone)

- Demo login only: username + password, every seeded user shares `SEED_PASSWORD`, no sign-up or password reset. Fine for a local demo; never deploy with the default `SECRET_KEY` or seeded passwords.
- The inbox updates by polling (every 5 s), not push.
- Filtering runs in Python after loading all profiles — fine for hackathon scale.
- Edit Profile accepts JPEG, PNG and WebP photos up to 5 MB. Uploads are saved with the profile, stored as bytes on the user record, and served through `/api/profiles/<id>/photo`. Uploaded photos take priority over the optional avatar URL, with initials as a fallback.
