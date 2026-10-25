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
| Database | SQLite in local dev, **PostgreSQL in production** (Neon on Vercel, `psycopg` driver). Same SQLAlchemy models and migrations for both |
| Hosting | Vercel: one project, `vercel.json` Services (`/api/*` → Flask, everything else → the Vite build). See [`docs/DEPLOY.md`](docs/DEPLOY.md) |
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
| `DATABASE_URL` | *(empty → `backend/instance/mogmatch.db`)* | Database to use. Empty = local SQLite file. A Postgres URL (`postgresql://user:pass@host/db`, or `postgres://...`) is used with the psycopg driver automatically. `POSTGRES_URL` also works (Vercel/Neon sets both) |
| `TEST_DATABASE_URL` | *(empty → temporary SQLite)* | Run `pytest` against this Postgres database instead. **It drops every table first**, so only use a throwaway DB |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Origins allowed to call `/api/*` |
| `DEMO_USER_EMAIL` | `demo@mogmatch.dev` | The seeded demo user (username `jordan-dev`) |
| `SECRET_KEY` | `dev-only-not-secret` | Signs the login cookie. **Required on Vercel**: the app refuses to start there with the default |
| `SEED_PASSWORD` | see `.env.example` | Password `flask seed` gives every seeded user |
| `PORT` | `5001` | Port for `python run.py` (5000 clashes with AirPlay on macOS) |

**`frontend/.env.local`**
| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `http://localhost:5001` in dev, empty in production builds | Flask API base URL. Leave unset on Vercel: production calls `/api` on the same domain |

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
| 25 demo users, e.g. `gigachad`, `seniorsam`, `midmike`, `juniorjo`, `newbie` | `123` | Only after `flask seed-test-users`. Five per Mog tier, from 👑 Gigamogger (100) down to 🥚 Hello World (5). Full list: `backend/app/demo_users.py` |

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
| `flask seed-test-users [--reset]` | Add (or recreate) `user1` / `user2` and 25 demo users across every Mog tier (password `123`). Local only |
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
  "theme": {"background": "#172554", "effect": null, "effect_options": {"brightness": 40, "size": 14, "speed": 4, "glow": false, "count": 1, "color_change": true, "color": "#ffffff", "rain_color": "#22ff66", "rain_rainbow": false, "rain_symbols": "katakana", "emojis": ["🚀", "✨", "🔥", "💻", "🦄", "🍕"], "emoji_count": 14, "emoji_angle": 45, "emoji_path": "straight", "emoji_spin": 2, "slogans": ["NEVER SKIP LEG DAY", "ONE MORE REP", "LIGHT WEIGHT BABY", "DO YOU EVEN LIFT?", "MOGGED"], "slogan_color": "#ff4d2e", "slogan_style": "mixed", "slogan_tilt": -8, "slogan_alternate": true, "chart_volatility": 6, "chart_mood": "choppy", "chart_palette": "classic", "chart_ticker": "MOG", "chart_label": true, "money_kind": "bills", "money_count": 30, "money_wind": 5, "money_weight": 5, "snow_kind": "mixed", "snow_count": 80, "snow_wind": 2}},
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
  - `theme.effect`: an animation drawn behind the card: `matrix` (falling green code), `dvd` (a bouncing DVD logo that changes color on every wall hit) `emoji` (emoji floating around, each one spinning) `slogans` (gym-bro slogans scrolling past in rows like a marquee) `market` (a made-up candlestick chart with pumps and crashes; it is not real data) `money` (green bills, or coins, fluttering down while gusts of wind blow them around) or `snow` (soft flakes and crystals drifting down on a wind that surges and eases off). All are generated in the browser on a canvas, not images. Any other name is a `400` with a `theme.effect` field error.
  - `theme.effect_options` tunes whichever effect is on; send any subset and the rest use the defaults shown above (responses always include every option). An effect ignores options that don't apply to it. They are kept while `effect` is `null`. Anything invalid is a `400` with a `theme.effect_options.<name>` field error.
    - Whole numbers: `brightness` 10-100 (%), `size` 10-48 (letter size for `matrix`, logo size for `dvd`), `speed` 1-10, `count` 1-10 (how many `dvd` logos).
    - `glow` true/false (neon halo). `color_change` true/false (`dvd`: a logo takes a new color on every bounce). `color` `#rrggbb` (`dvd`: the logo color while `color_change` is false).
    - `matrix` only: `rain_color` `#rrggbb` (default classic green); `rain_rainbow` true/false (every column gets its own drifting hue instead of `rain_color`); `rain_symbols` one of `katakana` (default), `binary`, `code`, `chaos`. The characters themselves live in the frontend (`RAIN_SYMBOLS` in `utils/theme.ts`).
    - `emoji` only: `emojis` a list of 1-12 emoji (default 🚀 ✨ 🔥 💻 🦄 🍕; duplicates are dropped, and only a rough check is made: short, no letters, digits, spaces or ASCII); `emoji_count` 3-60 (how many float at once); `emoji_angle` 0-359 (direction of travel in degrees: 0 is right, 90 is down); `emoji_path` one of `straight` (default; leaves one side, comes back in the other), `wave` (the same, wobbling side to side) or `bounce` (ricochets off the edges, starting along `emoji_angle`); `emoji_spin` -10 to 10 (tenths of a turn per second, negative is counter-clockwise, 0 is no spin). `size`, `speed`, `brightness` and `glow` apply too.
    - `slogans` only: `slogans` a list of 1-8 slogans of 1-40 characters each (default "NEVER SKIP LEG DAY", "ONE MORE REP", ...; whitespace is tidied, repeats ignoring case are dropped, and control or text-direction characters are rejected); `slogan_color` `#rrggbb`; `slogan_style` one of `solid`, `outline`, `mixed` (default; filled and outlined rows take turns); `slogan_tilt` -45 to 45 (degrees the rows lean; negative leans up to the right); `slogan_alternate` true/false (every other row scrolls the opposite way). `size` is the text size, and `speed`, `brightness` and `glow` apply too.
    - `market` only: `chart_volatility` 1-10 (how wildly the price swings); `chart_mood` one of `bull`, `bear`, `choppy` (default; which way it tends to go); `chart_palette` one of `classic` (default, green up and red down), `swapped`, `neon`, `mono`; `chart_ticker` 1-8 letters or numbers (trimmed, stored uppercase, default `MOG`); `chart_label` true/false (show the ticker, price and price tag). `size` is the candle width, and `speed`, `brightness` and `glow` apply too.
    - `money` only: `money_kind` one of `bills` (default; green bills that flip over as they fall), `coins` (gold and silver coins that spin) or `mixed` (both); `money_count` 5-80 (how many are in the air at once, default 30); `money_wind` 0-10 (how hard the gusts blow them sideways, and sometimes up; 0 is still air so they just fall, default 5); `money_weight` 1-10 (how heavy the coins are, default 5: heavier coins fall faster, turn over slower and are blown about less; bills ignore it). `size` is the bill length (a coin is about half that wide), `speed` is how fast they fall, and `brightness` and `glow` apply too.
    - `snow` only: `snow_kind` one of `dots` (soft round flakes), `crystals` (six-armed snowflakes that slowly turn) or `mixed` (default; both); `snow_count` 20-200 (how many are in the air at once, default 80); `snow_wind` -10 to 10 (which way the wind blows them: negative is left, positive is right, 0 is calm, default 2; the wind surges and eases off, so it is never perfectly steady). `size` is the flake size (a crystal is bigger than a soft flake of the same size), `speed` is how fast they fall, and `brightness` and `glow` apply too.
    - Colors are strict `#rrggbb` and, unlike `theme.background`, have no darkness rule: they are drawn on a canvas, never used as a fill behind text.
  - A `dvd` logo that lands in a corner (or bounces close enough to one, heading into it) sets off a sparkle burst; that part is not configurable.
- A theme saved by an older version whose effect or options no longer exist is read back as the default look (the stale values are ignored, not an error).
- `400` on invalid data or unknown fields, `409` if the username is taken.

## Deploying

Production is Vercel + Postgres; the full step-by-step guide, including how to run migrations against production, is in [`docs/DEPLOY.md`](docs/DEPLOY.md). In short:
1. Import the repo into Vercel with the repo root as the root directory (`vercel.json` defines both services).
2. Connect a Neon Postgres database (sets `DATABASE_URL`) and set `SECRET_KEY` and `SEED_PASSWORD`.
3. From your laptop: `DATABASE_URL="<production url>" flask db upgrade`, then the same with `flask seed`.
4. Deploy, then open `/api/health`.

Local dev stays on SQLite; to try Postgres locally, put a Postgres `DATABASE_URL` in `backend/.env`.

## Known limitations (this milestone)

- Demo login only: username + password, every seeded user shares `SEED_PASSWORD`, no sign-up or password reset. Fine for a local demo; never deploy with the default `SECRET_KEY` or seeded passwords.
- The inbox updates by polling (every 5 s), not push.
- Filtering runs in Python after loading all profiles — fine for hackathon scale.
- Edit Profile accepts JPEG, PNG and WebP photos up to 4 MB (Vercel rejects request bodies over 4.5 MB). Uploads are saved with the profile, stored as bytes on the user record, and served through `/api/profiles/<id>/photo`. Uploaded photos take priority over the optional avatar URL, with initials as a fallback.
