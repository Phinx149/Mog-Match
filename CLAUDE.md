# CLAUDE.md

Context for Claude Code working in this repo.

## Project
MogMatch — a developer matchmaking web app (hackathon theme: *Connect & Intersect*). Users have technical profiles, discover other devs, filter by skills/interests, and will later match. Planned differentiator: the **Intersect Engine** (recommends projects two devs could build together). Three-person, 24-hour hackathon: favor simple, working code.

See `README.md` for setup, API docs and current scope; `docs/` for product/architecture/roadmap.

## Stack
- `frontend/`: React 19 + Vite + TypeScript (strict), Tailwind CSS v4 (`@tailwindcss/vite`, theme tokens in `src/index.css`), React Router 7, lucide-react.
- `backend/`: Flask app factory, Flask-SQLAlchemy, Flask-Migrate (Alembic, batch mode for SQLite), Flask-CORS, python-dotenv. SQLite in dev.
- No Docker, Redis, or extra infra. Don't add large UI libraries.

## Commands
Backend (from `backend/`, venv active — Windows: `.venv\Scripts\...`):
- `python run.py` — API on :5001
- `pytest`
- `flask db migrate -m "msg"` / `flask db upgrade`
- `flask seed` / `flask seed --reset`

Frontend (from `frontend/`):
- `npm run dev` — :5173 (strict port; CORS allowlist expects it)
- `npm run typecheck` / `npm run build`

## Conventions
- Backend: routes stay thin; logic + validation + serialization live in `app/services/`. JSON field names are snake_case and match `frontend/src/types/profile.ts` — change both together.
- Errors: `{"error": {"message", "fields?"}}` with proper status codes (400 validation, 404, 409 conflict).
- Models use `db.Uuid` primary keys and `db.JSON` list columns (portable to Postgres). Assign a new list when updating JSON columns. Schema change → `flask db migrate`, review the generated file, commit it.
- `/api/profiles/me` resolves the user from server config (`DEMO_USER_EMAIL`). Never trust a client-supplied user id for "who am I".
- Seed must stay idempotent; destructive behavior only behind `--reset`.
- Frontend: pages in `src/pages/`, reusable UI in `src/components/<area>/`, all HTTP in `src/services/api.ts`. Handle loading/error/empty states.
- Every backend change keeps `pytest` green; every frontend change keeps `npm run build` green.

## Out of scope for the current milestone
Intersect Engine / AI recommendations, Mog Score, persistent swipes/matching, chat, voice, GitHub OAuth, real auth, payments.

## Team
Some contributors are beginners. Explain *why*, keep changes small, prefer readable code.
