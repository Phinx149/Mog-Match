# Architecture

The key decisions behind MogMatch and why we made them. How-to material (setup, commands, API reference, code map) is in [DEVELOPMENT.md](DEVELOPMENT.md); deployment steps are in [DEPLOY.md](DEPLOY.md).

## System at a glance

```
           Browser: React SPA (Vite, TypeScript, Tailwind)
              │  HTTP /api/*  +  Socket.IO /socket.io/*   (same origin, login cookie)
              ▼
           Flask API: routes → services → SQLAlchemy models
              │                         └─ OpenAI (AI project studio, optional)
              ▼
           SQLite (local dev)  /  PostgreSQL on Neon (production)

Production: one Vercel project, two Services:  /api/* + /socket.io/* → Flask,  everything else → static Vite build
```

```
users 1─1 profiles ─┬─< profile_links, projects
                    ├─< swipes   (me → them: like | pass)        a like = "they're on my Match page"
                    ├─< invites  (me → them: pending | accepted | declined, + team_mog)
                    │        └─< chat_messages, project_ideas, studio_turns   (an accepted invite is the chat)
                    └─< user_blocks
```

## Decisions

**1. One domain in production (Vercel Services).** The SPA and the API are served from the same origin: `/api/*` and `/socket.io/*` go to Flask, everything else to the static build. That makes the login cookie first-party (no third-party-cookie or CORS problems) and lets the frontend call relative `/api`. Locally they run as two processes, with CORS on, credentials allowed, on a fixed origin list.

**2. Thin routes, logic in services.** Routes only parse the request, call a service and return JSON. Validation, permissions and serialization live in `app/services/`, so they're testable without HTTP and reused by both the REST API and the Socket.IO handlers. Errors always look like `{"error": {"message", "fields?"}}` with real status codes (400 / 401 / 404 / 409).

**3. "Me" comes only from a signed session cookie.** Login stores the user id in Flask's signed, `HttpOnly`, `SameSite=Lax` cookie (`Secure` in production). Every "me" route calls `current_profile_or_401()`; the client never sends its own user id, and someone else's row is answered with a 404, not a 403, so ids can't be probed. Passwords are salted `werkzeug` hashes. The app refuses to start in production with the default `SECRET_KEY`.

**4. One portable data layer: SQLite for dev, Postgres for production.** Same SQLAlchemy models and Alembic migrations for both: `db.Uuid` keys, `db.JSON` lists, timezone-aware timestamps, ORM only (no raw SQL). Nobody needs a database server to develop. The catch: Postgres rejects strings longer than `String(n)`, so validation limits must stay at or under column sizes (a test checks this). The test suite runs on either database (`TEST_DATABASE_URL`).

**5. The database sets itself up on deploy.** Each Vercel build runs `backend/vercel_build.py`: migrations, then an idempotent seed that only adds what's missing and never overwrites edits. So migrations must be additive (add first, remove in a later release). Demo accounts with public passwords are opt-in (`SEED_DEMO_USERS=1`), and preview deployments get their own Neon branch so a PR can't touch production data.

**6. One kind of like.** A like is a row in `swipes`; liking from Discover or from a profile page is the same action. Matches are one-sided ("everyone I liked", ranked by similarity) so the demo works without waiting for the other person. Mutual intent happens one step later, through **invites**: one per pair, only the recipient can answer, and an *accepted* invite becomes the connection that chat, the AI studio, unmatch/rematch and the Team Mog Score hang off. Blocking hides both people from each other's Discover, likes and invites.

**7. Scores are pure functions, computed on read.** `mog_score.py`, `mog_match.py` and `team_mog.py` take plain dicts and return numbers plus their explanation, with no database or HTTP. They're cheap at our scale, always match the current profile, and are easy to unit-test and tune. The one exception is the Team Mog Score, saved on the invite when it's accepted so the reveal doesn't change afterwards. Rules: [MOG_SCORE.md](MOG_SCORE.md), [MOG_MATCH.md](MOG_MATCH.md).

**8. Real-time with Socket.IO, re-fetching as the safety net.** Chat messages and inbox changes are pushed over Socket.IO, and pages re-fetch when the tab regains focus, so nothing is lost if a socket drops. Sockets are tied to the session and disconnected on logout or account switch. Known limit: serverless functions are short-lived and requests may hit different instances, so live updates are best-effort on Vercel (messages are always saved). Details: [CHAT.md](CHAT.md).

**9. Cosmetic data is validated strictly, rendered in the browser.** Profile themes are one JSON column (`background`, `effect`, `effect_options`). The server checks every value (strict `#rrggbb`, a darkness limit so text stays readable, number ranges, emoji and slogan rules) because they end up in style attributes and canvases. All seven effects are drawn client-side on a canvas: nothing heavy is stored or served.

**10. Simple storage over extra infrastructure.** Profile photos are bytes on the `users` row (Postgres `bytea`), served by the API: no object storage to set up. Capped at 4 MB because Vercel rejects request bodies over 4.5 MB. Filtering and search run in Python over all profiles, which is fine at hackathon scale; move them into SQL if the user count grows.

**11. AI is a server-side, optional add-on.** The project studio and idea generator call OpenAI from the backend with a server-held key, so the key never reaches the browser. Without `OPENAI_API_KEY`, those features return a clear 503 and everything else works.

**12. Frontend: one API client, one auth source.** Every HTTP call goes through `services/api.ts` (sends the cookie, normalizes errors, turns any 401 into a logout). `AuthProvider` owns "who is logged in", re-checks it when a tab regains focus (tabs share one cookie), and `RequireAuth` guards every page except login and sign-up. Pages handle their own loading / error / empty states.

## Trade-offs we accepted (for a 24-hour hackathon)

- Usernames and passwords only: no email verification, password reset or rate limiting.
- One-sided matches instead of mutual swipes, for a demo that works with one real user.
- Best-effort real-time on serverless instead of a dedicated socket server.
- In-memory filtering and score computation instead of SQL indexes or caches.
