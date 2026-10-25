# MogMatch 💜

> A developer matchmaking platform. Build a technical profile, discover other developers, filter by skills and interests — and (soon) match with people whose skills *intersect* with yours.

Built for the Social Coding Hackathon — theme **Connect & Intersect**. Our headline feature (coming in a later milestone) is the **Intersect Engine**: it looks at two developers' complementary skills and shared interests and recommends projects they could build together.

## Current milestone

✅ Profiles stored in SQLite · ✅ Profile page · ✅ Edit profile (persists) · ✅ Discover page with search + skill filters · ✅ Like/Pass (in memory only) · ✅ Mog Score (on every profile, plus a Discover tier filter and sort)

⏳ Later: persistent swipes & matches, Intersect Engine, Team Mog Score, chat, voice, GitHub login.

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
│   │   ├── config.py            # env-driven config (DATABASE_URL, CORS_ORIGINS, DEMO_USER_EMAIL)
│   │   ├── extensions.py        # db, migrate (+ SQLite foreign keys on)
│   │   ├── models/              # User, Profile, ProfileLink, Project
│   │   ├── routes/              # health.py, profiles.py
│   │   ├── services/            # profile_service.py: filtering, validation, serialization
│   │   └── seed.py              # `flask seed` command + sample data
│   ├── migrations/              # Alembic migrations (Flask-Migrate)
│   ├── tests/                   # pytest
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/          # layout/, profiles/, discover/, forms/, common/
│   │   ├── pages/               # Discover, Profile, EditProfile, Settings, NotFound
│   │   ├── services/api.ts      # typed fetch wrapper for the Flask API
│   │   ├── types/profile.ts     # TS interfaces matching API responses
│   │   ├── hooks/
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
flask seed              # demo user + 10 developers
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
python run.py
```

> `flask` commands find the app through `FLASK_APP=run.py` in `.env`. Run them from `backend/` with the venv active.

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
```
Seeds one **demo user** (Jordan Avery, the "you" of the app) plus 10 developers across frontend, backend, full-stack, AI/ML, game dev, cybersecurity, data engineering, mobile and DevOps.

## Running locally

Two terminals:
1. `backend/` → activate venv → `python run.py`
2. `frontend/` → `npm run dev`

Open http://localhost:5173. The green **ping** pill in the top bar confirms the frontend can reach the API.

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

- Demo login only: username + password, every seeded user shares `SEED_PASSWORD`, no sign-up. Test two users at once with a normal and an incognito window. Open the app at `localhost:5173` (not `127.0.0.1`) so the login cookie reaches the API on `localhost:5001`.
- Likes/passes reset on page reload (React state only).
- Filtering runs in Python after loading all profiles — fine for hackathon scale.
- Edit Profile accepts JPEG, PNG and WebP photos up to 5 MB. Uploads are saved with the profile, stored as bytes on the user record, and served through `/api/profiles/<id>/photo`. Uploaded photos take priority over the optional avatar URL, with initials as a fallback.
