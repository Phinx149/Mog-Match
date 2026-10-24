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
   - `flask db upgrade` → `flask seed` → `python run.py` (port 5001)
   - Verify: open http://localhost:5001/api/health → `{"status":"ok","database":"ok"}`
3. Frontend (in `frontend/`):
   - `npm install`, copy `.env.example` → `.env.local`, `npm run dev` (port 5173)
   - Verify: http://localhost:5173 shows Discover with profiles and a green **ping** pill.
4. Practice the git flow from `CONTRIBUTING.md` with a tiny PR (add their name to the Team table in `docs/ROADMAP.md`).

## Common problems
| Symptom | Fix |
|---|---|
| `flask: command not found` / `Could not locate a Flask application` | venv not active, or not in `backend/`, or `.env` missing `FLASK_APP=run.py` |
| PowerShell: `running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, reopen terminal |
| `no such table: profiles` | run `flask db upgrade` |
| Discover says "No developers match" with no filters | run `flask seed` |
| `Demo profile not found` | `flask seed`; check `DEMO_USER_EMAIL` in `.env` matches the seeded email |
| Ping pill red / "Can't reach the API" | Flask not running, or `VITE_API_URL` in `frontend/.env.local` has the wrong port — restart `npm run dev` after editing env files |
| Browser console CORS error | frontend not on `http://localhost:5173`; add its origin to `CORS_ORIGINS` in `backend/.env` and restart Flask |
| `Port 5173 is already in use` | another Vite is running; stop it (strictPort is on so CORS stays correct) |
| macOS: port 5000 busy | we use 5001 already; change `PORT` in `.env` if needed (and `VITE_API_URL`) |
| Local DB in a weird state | stop Flask, delete `backend/instance/mogmatch.db`, `flask db upgrade && flask seed` |
