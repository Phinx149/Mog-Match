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
| `DEMO_USER_EMAIL` | `demo@mogmatch.dev` | The seeded user `/api/profiles/me` acts as |
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
| GET | `/api/profiles` | Discoverable profiles (excludes the demo user) → `{"profiles": [...], "count": n}` |
| GET | `/api/profiles/filter-options` | Every allowed value for the list fields → `{"skills": [...], "looking_for": [...]}`. Powers the Discover filter menu and the Edit Profile "Looking for" picker |
| GET | `/api/profiles/<uuid>` | One profile, `404` if missing |
| GET | `/api/profiles/me` | The demo user's profile |
| PATCH | `/api/profiles/me` | Partial update of the demo user's profile |

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
  "theme": {"background": "#172554", "effect": null, "effect_options": {"brightness": 40, "size": 14, "speed": 4, "glow": false, "count": 1, "color_change": true, "color": "#ffffff", "rain_color": "#22ff66", "rain_rainbow": false, "rain_symbols": "katakana", "emojis": ["🚀", "✨", "🔥", "💻", "🦄", "🍕"], "emoji_count": 14, "emoji_angle": 45, "emoji_path": "straight", "emoji_spin": 2, "slogans": ["NEVER SKIP LEG DAY", "ONE MORE REP", "LIGHT WEIGHT BABY", "DO YOU EVEN LIFT?", "MOGGED"], "slogan_color": "#ff4d2e", "slogan_style": "mixed", "slogan_tilt": -8, "slogan_alternate": true, "chart_volatility": 6, "chart_mood": "choppy", "chart_palette": "classic", "chart_ticker": "MOG", "chart_label": true}},
  "links": [{"id": "uuid", "label": "GitHub", "url": "https://..."}],
  "projects": [{"id": "uuid", "title": "Prism UI", "description": "...", "project_url": "https://...", "technologies": ["React"]}],
  "created_at": "ISO-8601", "updated_at": "ISO-8601"
}
```

**`PATCH /api/profiles/me`** accepts any subset of: `full_name`, `username`, `avatar_url`, `location`, `education`, `bio`, `favorite_ide`, `experience_level` (`Student | Junior | Mid-level | Senior | Lead`), `skills`, `interests`, `favorite_ai_agents`, `looking_for` (fixed list, see below), `links` (`[{label, url}]`), `projects` (`[{title, description, project_url, technologies}]`), `theme` (`{background, effect, effect_options}`).
- `links`, `projects` and `theme`, when sent, **replace** the existing value.
- Tags are trimmed and de-duplicated (case-insensitive). URLs must be `http(s)`.
- `skills` must come from the tech catalog and `looking_for` from `Hackathon team | Side project | Open source | Cofounder | Mentor | Mentee | Just vibes` (case-insensitive; stored with the canonical spelling). `GET /api/profiles/filter-options` returns both lists.
- `theme` is cosmetic only; nothing else (search, filters, Mog Score) reads it. Each option is `null` for the default look.
  - `theme.background`: `#rrggbb`. It must be dark enough for the light text to stay readable, otherwise `400` with a `theme.background` field error.
  - `theme.effect`: an animation drawn behind the card: `matrix` (falling green code), `dvd` (a bouncing DVD logo that changes color on every wall hit) `emoji` (emoji floating around, each one spinning) `slogans` (gym-bro slogans scrolling past in rows like a marquee) or `market` (a made-up candlestick chart with pumps and crashes; it is not real data). All are generated in the browser on a canvas, not images. Any other name is a `400` with a `theme.effect` field error.
  - `theme.effect_options` tunes whichever effect is on; send any subset and the rest use the defaults shown above (responses always include every option). An effect ignores options that don't apply to it. They are kept while `effect` is `null`. Anything invalid is a `400` with a `theme.effect_options.<name>` field error.
    - Whole numbers: `brightness` 10-100 (%), `size` 10-48 (letter size for `matrix`, logo size for `dvd`), `speed` 1-10, `count` 1-10 (how many `dvd` logos).
    - `glow` true/false (neon halo). `color_change` true/false (`dvd`: a logo takes a new color on every bounce). `color` `#rrggbb` (`dvd`: the logo color while `color_change` is false).
    - `matrix` only: `rain_color` `#rrggbb` (default classic green); `rain_rainbow` true/false (every column gets its own drifting hue instead of `rain_color`); `rain_symbols` one of `katakana` (default), `binary`, `code`, `chaos`. The characters themselves live in the frontend (`RAIN_SYMBOLS` in `utils/theme.ts`).
    - `emoji` only: `emojis` a list of 1-12 emoji (default 🚀 ✨ 🔥 💻 🦄 🍕; duplicates are dropped, and only a rough check is made: short, no letters, digits, spaces or ASCII); `emoji_count` 3-60 (how many float at once); `emoji_angle` 0-359 (direction of travel in degrees: 0 is right, 90 is down); `emoji_path` one of `straight` (default; leaves one side, comes back in the other), `wave` (the same, wobbling side to side) or `bounce` (ricochets off the edges, starting along `emoji_angle`); `emoji_spin` -10 to 10 (tenths of a turn per second, negative is counter-clockwise, 0 is no spin). `size`, `speed`, `brightness` and `glow` apply too.
    - `slogans` only: `slogans` a list of 1-8 slogans of 1-40 characters each (default "NEVER SKIP LEG DAY", "ONE MORE REP", ...; whitespace is tidied, repeats ignoring case are dropped, and control or text-direction characters are rejected); `slogan_color` `#rrggbb`; `slogan_style` one of `solid`, `outline`, `mixed` (default; filled and outlined rows take turns); `slogan_tilt` -45 to 45 (degrees the rows lean; negative leans up to the right); `slogan_alternate` true/false (every other row scrolls the opposite way). `size` is the text size, and `speed`, `brightness` and `glow` apply too.
    - `market` only: `chart_volatility` 1-10 (how wildly the price swings); `chart_mood` one of `bull`, `bear`, `choppy` (default; which way it tends to go); `chart_palette` one of `classic` (default, green up and red down), `swapped`, `neon`, `mono`; `chart_ticker` 1-8 letters or numbers (trimmed, stored uppercase, default `MOG`); `chart_label` true/false (show the ticker, price and price tag). `size` is the candle width, and `speed`, `brightness` and `glow` apply too.
    - Colors are strict `#rrggbb` and, unlike `theme.background`, have no darkness rule: they are drawn on a canvas, never used as a fill behind text.
  - A `dvd` logo that lands in a corner (or bounces close enough to one, heading into it) sets off a sparkle burst; that part is not configurable.
- A theme saved by an older version whose effect or options no longer exist is read back as the default look (the stale values are ignored, not an error).
- `400` on invalid data or unknown fields, `409` if the username is taken.

## Known limitations (this milestone)

- No authentication: `/me` is always the server-configured demo user.
- Likes/passes reset on page reload (React state only).
- Filtering runs in Python after loading all profiles — fine for hackathon scale.
- Edit Profile accepts JPEG, PNG and WebP photos up to 5 MB. Uploads are saved with the profile, stored as bytes on the user record, and served through `/api/profiles/<id>/photo`. Uploaded photos take priority over the optional avatar URL, with initials as a fallback.
