---
name: setup-project
description: Get a developer's local MogMatch environment running (Flask backend + React/Vite frontend + SQLite), or diagnose setup problems. Use when someone says "set up", "I just cloned", "how do I run this", "flask not found", "npm run dev fails", "ping says offline", or "CORS error".
---

# Setup Project

Full instructions live in `README.md` (Backend setup / Frontend setup). Walk the developer through them **one step at a time**, checking each command's output before moving on. Detect their OS first (Windows PowerShell vs macOS/Linux/WSL) and give the matching commands.

## Checklist
1. Versions: `python --version` (Windows: `py --version`) ≥ 3.12, `node -v` ≥ 20.19, `git --version`.
2. Backend (in `backend/`):
   - Create venv: `python3 -m venv .venv` / `py -3 -m venv .venv`
   - Activate: `source .venv/bin/activate` / `.venv\Scripts\Activate.ps1`
   - `pip install -r requirements.txt`
   - `cp .env.example .env` / `Copy-Item .env.example .env`
   - `flask db upgrade` → `flask seed` → (optional) `flask seed-test-users` → `python run.py` (port 5001)
   - Verify: open http://localhost:5001/api/health → `{"status":"ok","database":"ok"}`
3. Frontend (in `frontend/`):
   - `npm install`, copy `.env.example` → `.env.local`, `npm run dev` (port 5173)
   - Verify: http://localhost:5173 (use `localhost`, not `127.0.0.1`) shows the **login page**. Log in as `jordan-dev` with `SEED_PASSWORD` from `backend/.env.example` (or `user1` / `user2`, passwords in `TEST_USERS` in `backend/app/seed.py`). Discover should list profiles and show a green **ping** pill.
4. Already set up and just pulled? `pip install -r requirements.txt`, `flask db upgrade`, `flask seed`, `npm install`, restart both servers.
5. Practice the git flow from `CONTRIBUTING.md` with a tiny PR (add their name to the Team table in `docs/ROADMAP.md`).

## Common problems
| Symptom | Fix |
|---|---|
| `flask: command not found` / `Could not locate a Flask application` | venv not active, or not in `backend/`, or `.env` missing `FLASK_APP=run.py` |
| PowerShell: `running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, reopen terminal |
| `no such table: profiles` | run `flask db upgrade` |
| Discover says "No developers match" with no filters | run `flask seed` |
| `no such column: users.password_hash` / `no such table: invites` | `flask db upgrade` (new migrations since they last pulled) |
| "Wrong username or password" for a seeded account | `flask seed` (fills in missing passwords); check `SEED_PASSWORD` in `.env` vs `.env.example` |
| Every page bounces back to `/login` after logging in | they opened `127.0.0.1:5173`; use `http://localhost:5173` (cookie is per host) |
| API returns `401 Log in first.` | expected when logged out; log in at `/login`. After `flask seed --reset` everyone is logged out |
| Two tabs show the same user | normal tabs share one login; use an incognito window for a second user |
| Ping pill red / "Can't reach the API" | Flask not running, or `VITE_API_URL` in `frontend/.env.local` has the wrong port — restart `npm run dev` after editing env files |
| Browser console CORS error | frontend not on `http://localhost:5173`; add its origin to `CORS_ORIGINS` in `backend/.env` and restart Flask |
| `Port 5173 is already in use` | another Vite is running; stop it (strictPort is on so CORS stays correct) |
| macOS: port 5000 busy | we use 5001 already; change `PORT` in `.env` if needed (and `VITE_API_URL`) |
| `ModuleNotFoundError: psycopg` | `pip install -r requirements.txt` (Postgres driver, added for production) |
| Want to use Postgres locally | Put `DATABASE_URL=postgresql://...` in `backend/.env`, then `flask db upgrade && flask seed`. Default SQLite is fine for dev |
| Local DB in a weird state | stop Flask, delete `backend/instance/mogmatch.db`, `flask db upgrade && flask seed` |
