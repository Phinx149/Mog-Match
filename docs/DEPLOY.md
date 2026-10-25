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

   Don't set `VITE_API_URL` (production uses same-origin `/api`) or `CORS_ORIGINS` (not needed on one domain).
4. **Create the tables and demo data from your laptop.** Migrations don't run during the Vercel build, so you apply them yourself. Copy the database's connection string from Vercel (*Storage → your database → .env snippet*). Prefer the **unpooled / direct** URL for migrations if one is listed. Then, from `backend/` with the venv active:

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

## Every time the schema changes

When a merged PR adds a migration (a new file in `backend/migrations/versions/`), run `flask db upgrade` against the production `DATABASE_URL` as in step 4. Do it **before** the new code goes live if the migration only adds things (tables or nullable columns), which is the usual case. Check with `flask db current` (prints the applied revision) and `flask db heads` (the latest).

## Limits to know

- **Request bodies max out at 4.5 MB** on Vercel, so profile photos are capped at 4 MB (`MAX_PHOTO_BYTES` in `backend/app/config.py`).
- **Services is a beta feature.** If the `services` config ever stops working, the fallback is two Vercel projects (frontend and backend). That needs `CORS_ORIGINS` set to the frontend's URL and the login cookie to use `SameSite=None`, so stay on one project if you can.
- Functions sleep when idle; the first request after a while is slower (cold start). The DB pool pings connections before use (`pool_pre_ping`) so stale connections are replaced automatically.
- Seeded accounts all share `SEED_PASSWORD`, and there's no sign-up yet. Fine for a demo, not for real users.

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
| Can't log in as `jordan-dev` on production | `flask seed` wasn't run against production, or you're using the wrong `SEED_PASSWORD` |
| Refreshing `/inbox` gives a 404 | The `web` service's rewrite to `/index.html` in `vercel.json` is missing |
| Photo upload fails with 413 | The file is over Vercel's 4.5 MB limit; the app asks for ≤ 4 MB |
| `ModuleNotFoundError: psycopg` | `pip install -r requirements.txt` (psycopg is the Postgres driver) |
