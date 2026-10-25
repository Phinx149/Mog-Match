# Deploying to Vercel (with Postgres)

Production runs as **one Vercel project** with two [Services](https://vercel.com/docs/services) (beta), defined in `vercel.json` at the repo root:

```
https://<project>.vercel.app
  ├─ /api/*  → "api" service: Flask (backend/, entrypoint run:app) → Postgres (Neon)
  └─ /*      → "web" service: the Vite build of frontend/ (index.html for client-side routes)
```

Frontend and API share one domain, so the login cookie is first-party and CORS isn't involved. Flask receives the full path (`/api/profiles`), so routes are the same as in local dev. The frontend's production build calls relative `/api/...` (see `API_URL` in `frontend/src/services/api.ts`).

**Why Postgres:** Vercel functions have a read-only, throwaway filesystem, so the SQLite file used in local dev can't work there. The app refuses to start on Vercel without `DATABASE_URL`.

## One-time setup

1. **Create the project.** In Vercel: *Add New → Project*, import the GitHub repo, and keep the **root directory as the repo root** (where `vercel.json` is). Vercel picks up both services from `vercel.json`.
2. **Add a database.** In the project: *Storage → Create / Connect Database → Neon (Postgres)*, then connect it to the project. This sets `DATABASE_URL` (and `POSTGRES_URL`, which the app also accepts) for every environment.
3. **Set environment variables** (*Settings → Environment Variables*):

   | Variable | Value |
   |---|---|
   | `SECRET_KEY` | A long random string, e.g. the output of `python -c "import secrets; print(secrets.token_hex(32))"`. **Required**: the app won't start on Vercel with the dev default. |
   | `SEED_PASSWORD` | The password you'll give the seeded demo accounts. Use something other than the value in `.env.example`, because that file is public. |
   | `DATABASE_URL` | Set by the Neon integration. Leave it. |
   | `SEED_DEMO_USERS` | Optional. `1` also creates `user1`/`user2` and the 60 demo users (password `123`) on every deploy. Their passwords are public in this repo, so only use it for a demo. |
   | `OPENAI_API_KEY` | Needed for the AI project studio and project ideas in chat. Without it those features return "needs an OpenAI API key"; everything else works. `OPENAI_MODEL` is optional. |

   Don't set `VITE_API_URL` (production uses same-origin `/api`) or `CORS_ORIGINS` (not needed on one domain).
4. **Tables and demo data are created automatically on every deploy.** The `api` service's `buildCommand` (`python vercel_build.py` in `vercel.json`) runs migrations and `flask seed` before the new version goes live, and also `flask seed-test-users` when `SEED_DEMO_USERS=1`. Both are safe to repeat: they only add what's missing. Look for `[vercel_build] database ready` in the deployment's **Build Logs**. If you ever need to do it by hand (or the build step can't reach the database), run it from your laptop instead. Copy the database's connection string from Vercel (*Storage → your database → .env snippet*). Prefer the **unpooled / direct** URL for migrations if one is listed. Then, from `backend/` with the venv active:

   **macOS / Linux**
   ```bash
   DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require" flask db upgrade
   DATABASE_URL="postgresql://..." SEED_PASSWORD="<same as in Vercel>" flask seed
   ```
   **Windows (PowerShell)**
   ```powershell
   $env:DATABASE_URL = "postgresql://...neon.tech/neondb?sslmode=require"
   $env:SEED_PASSWORD = "<same as in Vercel>"
   flask db upgrade
   flask seed
   Remove-Item Env:DATABASE_URL, Env:SEED_PASSWORD   # back to your local SQLite
   ```
   Don't run `flask seed-test-users` against production (its passwords are in the repo).
5. **Deploy.** Push to the branch Vercel deploys (or click *Redeploy*). Open `https://<project>.vercel.app`, log in as `jordan-dev` with your `SEED_PASSWORD`, and check `https://<project>.vercel.app/api/health` says `"database": "ok"`.

> **Preview deployments run the build too.** If Preview and Production share one `DATABASE_URL`, a PR's preview applies that PR's migrations to the production database before it's merged. Give Preview its own database: Neon's integration can create a branch per preview, or set a separate `DATABASE_URL` for the Preview environment.

## Every time the schema changes

Nothing to do: each deploy applies new migrations during the build, before the new code goes live. That's right for migrations that only add things (tables, nullable columns), which is the usual case. If a migration removes or renames something the *current* live version still uses, deploy in two steps (add the new thing first, remove the old one in a later PR). Check with `flask db current` (prints the applied revision) and `flask db heads` (the latest).

## Limits to know

- **Request bodies max out at 4.5 MB** on Vercel, so profile photos are capped at 4 MB (`MAX_PHOTO_BYTES` in `backend/app/config.py`).
- **Services is a beta feature.** If the `services` config ever stops working, the fallback is two Vercel projects (frontend and backend). That needs `CORS_ORIGINS` set to the frontend's URL and the login cookie to use `SameSite=None`, so stay on one project if you can.
- **Live chat (Socket.IO) is best-effort on Vercel.** Functions are short-lived and requests can hit different instances, so long-polling sessions and WebSocket upgrades may drop. Reliable real-time chat needs a long-running server (or a hosted realtime service); saving and loading messages works regardless.
- Functions sleep when idle; the first request after a while is slower (cold start). The DB pool pings connections before use (`pool_pre_ping`) so stale connections are replaced automatically.
- Seeded accounts all share `SEED_PASSWORD`. Anyone can sign up (`/signup`), with no email verification, rate limiting or password reset. Fine for a demo, not for real users.

## Running against Postgres locally (optional)

Local dev uses SQLite by default; everything is written to work on both. To develop or test on Postgres:

- **Point the app at any Postgres** (a free Neon branch works, or a local server): put `DATABASE_URL=postgresql://user:pass@host:5432/dbname` in `backend/.env`, then `flask db upgrade && flask seed`.
- **Run the test suite on Postgres**: `TEST_DATABASE_URL=postgresql://... pytest` (PowerShell: `$env:TEST_DATABASE_URL="postgresql://..."; pytest`). It **drops every table** in that database first, so use an empty, throwaway database.

Postgres is stricter than SQLite in a few ways the code already handles; keep it that way:
- Text longer than a column's `String(n)` is an error on Postgres (SQLite stores it anyway), so every validation limit in `profile_service.py` / `invite_service.py` must be ≤ the column size. `tests/test_api.py::test_every_field_at_its_max_length_saves` guards this; run it with `TEST_DATABASE_URL` after changing limits or columns.
- Use the ORM (no raw SQL), `db.Uuid` and `db.JSON` columns, and timezone-aware datetimes (`TimestampMixin`).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Deploy logs: `Set DATABASE_URL` / `Set SECRET_KEY` | Add the variable in Vercel (*Settings → Environment Variables*) and redeploy |
| `relation "users" does not exist` / 500s on every request | Tables weren't created: run step 4 against the production `DATABASE_URL` |
| `column ... does not exist` after a deploy | A new migration wasn't applied to production: `flask db upgrade` with the production URL |
| Can't log in as `jordan-dev` on production | Check the Build Logs for `[vercel_build] seed: ...`. If it's missing, redeploy; if it failed, the error is right above it. Also check `SEED_PASSWORD` in Vercel matches the password you type |
| Demo users like `gigachad` don't exist | Set `SEED_DEMO_USERS=1` in Vercel and redeploy |
| Build fails with `Set DATABASE_URL` / `Set SECRET_KEY` | The build step needs them too: add them for the environment you're deploying (Production / Preview) |
| Chat messages don't arrive live / `Session ID unknown` in the console | Live chat uses Socket.IO, which keeps connections in one server's memory. Vercel can send each request to a different instance, so real-time chat may be unreliable there (messages still save). See "Limits to know" |
| Refreshing `/inbox` gives a 404 | The `web` service's rewrite to `/index.html` in `vercel.json` is missing |
| Photo upload fails with 413 | The file is over Vercel's 4.5 MB limit; the app asks for ≤ 4 MB |
| `ModuleNotFoundError: psycopg` | `pip install -r requirements.txt` (psycopg is the Postgres driver) |
