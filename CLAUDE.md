# CLAUDE.md

Context for Claude Code working in this repo.

## Project
MogMatch — a developer matchmaking web app (hackathon theme: *Connect & Intersect*). Users log in, have technical profiles, discover and like other devs (Mog Match ranks them by similarity), and send invites that land in the other person's Inbox. Next up: chat for accepted invites. Planned differentiator: the **Intersect Engine** (recommends projects two devs could build together). Three-person, 24-hour hackathon: favor simple, working code.

`README.md` is the public showcase (what the app does + the live link). Setup, environment variables, seed data, logins for testing, the API reference and the code map live in `docs/DEVELOPMENT.md`; the key design decisions (and why) are in `docs/ARCHITECTURE.md`, which stays short. `docs/` also has deploy, chat, scoring and roadmap notes. Keep the README about features, not setup.

## Stack
- `frontend/`: React 19 + Vite + TypeScript (strict), Tailwind CSS v4 (`@tailwindcss/vite`, theme tokens in `src/index.css`), React Router 7, lucide-react.
- `backend/`: Flask app factory, Flask-SQLAlchemy, Flask-Migrate (Alembic, batch mode for SQLite), Flask-CORS, python-dotenv. **SQLite in local dev, Postgres (psycopg 3) in production.**
- Deploy: Vercel, one project, `vercel.json` Services: `/api/*` → Flask (`backend/`, `run:app`), the rest → the Vite build. Guide: `docs/DEPLOY.md`.
- No Docker, Redis, or extra infra in the project. Don't add large UI libraries.

## Commands
Backend (from `backend/`, venv active — Windows: `.venv\Scripts\...`):
- `python run.py` — API on :5001
- `pytest`
- `flask db migrate -m "msg"` / `flask db upgrade`
- `flask seed` / `flask seed --reset`
- `flask seed-test-users [--reset]` — quick-login `user1` / `user2` (passwords in `TEST_USERS`, `app/seed.py`) that already like each other, plus 50 demo users (password `123`, `app/demo_users.py`), 10 per Mog tier. `tests/test_demo_users.py` checks each lands in its tier: rescore them if you change Mog Score weights. Every seeded account gets a profile picture (`app/seed_avatars/<username>.png`, redrawn by `scripts/make_seed_avatars.py`) and a theme; tests that need a plain default profile use the `blank_looks` fixture
- `flask db check` — fails if models and migrations disagree
- `TEST_DATABASE_URL=postgresql://... pytest` — same suite on Postgres (drops all tables in that DB; throwaway DBs only)
- After pulling: `pip install -r requirements.txt`, `flask db upgrade`, `flask seed`

Frontend (from `frontend/`):
- `npm run dev` — :5173 (strict port; CORS allowlist expects it)
- `npm run typecheck` / `npm run build`

## Conventions
- Backend: routes stay thin; logic + validation + serialization live in `app/services/`. JSON field names are snake_case and match `frontend/src/types/profile.ts` — change both together.
- Errors: `{"error": {"message", "fields?"}}` with proper status codes (400 validation, 404, 409 conflict).
- Models use `db.Uuid` primary keys and `db.JSON` list columns (portable to Postgres). Assign a new list when updating JSON columns. Schema change → `flask db migrate`, review the generated file, commit it.
- "Me" is the logged-in user from the signed session: `current_profile_or_401()` in every "me" route. Never trust a client-supplied user id for "who am I". Details in **Auth** below.
- Seed must stay idempotent; destructive behavior only behind `--reset`.
- Frontend: pages in `src/pages/`, reusable UI in `src/components/<area>/`, all HTTP in `src/services/api.ts`. Handle loading/error/empty states.
- Every backend change keeps `pytest` green; every frontend change keeps `npm run build` green.

## Database portability (SQLite locally, Postgres in production)
- Code must work on both. Use the ORM only (no raw SQL, no SQLite-only functions), `db.Uuid` / `db.JSON` columns, `TimestampMixin` datetimes.
- Postgres errors on strings longer than `String(n)`; SQLite doesn't. Every validation limit must be ≤ its column size (`test_every_field_at_its_max_length_saves` checks).
- New migration → also try it on Postgres before merging if you can: `DATABASE_URL=postgresql://... flask db upgrade` on an empty DB, or run the tests with `TEST_DATABASE_URL`. Production applies it automatically on the next deploy (`backend/vercel_build.py`, the api service's `buildCommand`), so keep migrations additive.
- Vercel limits: read-only disk (never write files at runtime), 4.5 MB request bodies (photos capped by `MAX_PHOTO_BYTES`), cold starts. `create_app` refuses to start on Vercel (`VERCEL=1`) without `DATABASE_URL` or with the default `SECRET_KEY`.

## Auth (how "me" works)
- Login and sign-up are username + password: `app/services/auth_service.py`, routes in `app/routes/auth.py` (`POST /api/auth/login`, `POST /api/auth/signup`, `POST /api/auth/logout`, `GET /api/auth/session`). Sign-up creates a `User` plus a nearly empty `Profile` and logs the browser in; the frontend then sends the new user to `/profile/edit`. Passwords are `werkzeug.security` hashes in `users.password_hash`; the session is Flask's signed cookie holding `user_id` (`SECRET_KEY` in config).
- New "me" route: `me = current_profile_or_401()` (from `..services.auth_service`), then pass `me` to a service. Logged out → `401 {"error": {"message": "Log in first."}}`. Don't read identity from the request body or query string, and don't reintroduce `DEMO_USER_EMAIL` lookups (`DEMO_USER_EMAIL` only marks which seeded account is the demo user).
- Tests (`tests/conftest.py`): `client` is logged in as `jordan-dev`, `anon_client` is logged out, `log_in(client, "samfullstack")` logs a client in as anyone seeded. For two users, make two clients: `a = log_in(app.test_client(), "jordan-dev")`, `b = log_in(app.test_client(), "samfullstack")`. `flask seed --reset` recreates users, so log in again after it (see `test_api.py`). Password checks are slow on purpose (~0.1 s per login), so the suite takes ~30 s.
- Frontend: `useAuth()` (`src/hooks/useAuth.tsx`) gives `user`, `logIn`, `signUp`, `logOut`. Routes inside `<RequireAuth />` in `App.tsx` need a login; `/login` and `/signup` are outside it. `request()` in `api.ts` sends the cookie (`credentials: "include"`) and fires `LOGGED_OUT_EVENT` on any `401`.
- Gotchas: open the app at `localhost:5173`, not `127.0.0.1` (the cookie is per host). On Vercel the cookie is also `Secure` (HTTPS only). Normal browser tabs share one login, so test two users with a normal and an incognito window. Seeded passwords and the default `SECRET_KEY` are demo-only.

## Verifying a change end-to-end
`flask seed --reset && flask seed-test-users --reset` gives a known state. Then exercise the running API with two cookie jars (two users), or log in at http://localhost:5173 as `user1` (normal window) and `user2` (incognito). Reset again afterwards so teammates aren't left with your test data.

## Out of scope for the current milestone
Intersect Engine / AI recommendations, Team Mog Score, voice, GitHub OAuth, password reset / email verification, payments. (Chat for accepted invites is the next planned feature; see `docs/ROADMAP.md`.)

## Team
Some contributors are beginners. Explain *why*, keep changes small, prefer readable code.
