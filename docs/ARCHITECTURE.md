# Architecture

## Overview
```
 Browser ── React SPA (Vite, :5173)
              │  fetch JSON  (src/services/api.ts, VITE_API_URL)
              ▼
 Flask API (:5001)  app factory in backend/app/__init__.py
   ├─ routes/      thin HTTP layer (health, auth, profiles, swipes, invites)
   ├─ services/    validation, filtering, serialization
   ├─ models/      SQLAlchemy models
   └─ seed.py      `flask seed` CLI
              │  SQLAlchemy ORM
              ▼
 SQLite (backend/instance/mogmatch.db)  ── or PostgreSQL via DATABASE_URL
```

Monorepo, two processes in dev. CORS on `/api/*` allows the Vite origin(s) from `CORS_ORIGINS`, **with credentials**, so the browser sends the login cookie (`fetch(..., {credentials: "include"})` in `api.ts`).

## Data model

```
users ──1:1── profiles ──1:N── profile_links
                     ├──1:N── projects
                     ├──N:N── swipes   (swiper → target, like | pass)
                     └──N:N── invites  (sender → recipient, pending | accepted | declined)
```

| Table | Columns |
|---|---|
| `users` | `id` UUID PK, `email` unique nullable, `password_hash` (werkzeug salted hash, null = can't log in), `photo_data`, `photo_mimetype`, `created_at`, `updated_at` |
| `profiles` | `id` UUID PK, `user_id` FK→users (unique, cascade), `full_name`, `username` unique, `avatar_url`, `location`, `education`, `bio`, `favorite_ide`, `experience_level`, JSON lists: `skills`, `interests`, `favorite_ai_agents`, `looking_for`, timestamps |
| `profile_links` | `id` UUID PK, `profile_id` FK (cascade), `label`, `url`, `position` |
| `projects` | `id` UUID PK, `profile_id` FK (cascade), `title`, `description`, `project_url`, JSON `technologies`, `position`, timestamps |
| `swipes` | `id` UUID PK, `swiper_id` / `target_id` FK→profiles (cascade), `action` `like`\|`pass`, timestamps. Unique (`swiper_id`, `target_id`): swiping again overwrites |
| `invites` | `id` UUID PK, `sender_id` / `recipient_id` FK→profiles (cascade), `message` (≤280, nullable), `status` `pending`\|`accepted`\|`declined`, timestamps. Unique (`sender_id`, `recipient_id`); the service also blocks the reverse direction |

Deleting a profile removes its swipes and invites in both directions (ORM cascades on `Profile`, since SQLite doesn't enforce `ON DELETE CASCADE` by default).

The original hand-drawn schema (`id, users_id, loc, langs, fav_ide, fav_agents`) maps to `profiles.id`, `profiles.user_id`, `location`, `skills` (languages are skills), `favorite_ide`, `favorite_ai_agents`.

**Portability:** `db.Uuid` → native `uuid` on Postgres, `CHAR(32)` on SQLite. `db.JSON` → `json` on Postgres. No SQLite-only SQL anywhere.

### Planned tables (later milestones)
```
messages (id, invite_id → invites (accepted only), sender_id → profiles, body, created_at)   chat
```
An accepted invite is the "connection" two people chat in; the Intersect Engine's project ideas can hang off it too.

## Request flow examples

**Discover:** `DiscoverPage` → debounced `listProfiles({q, skills})` → `GET /api/profiles?q=..&skills=..` → `profile_service.list_profiles` (filters in Python, excludes demo profile) → `{profiles, count}`. Like/Pass → `POST /api/swipes` (saved in `swipes`); swiped profiles are left out of the list. Everyone liked shows on the Match page (`GET /api/profiles/me/matches`).

**Log in:** `LoginPage` → `POST /api/auth/login {username, password}` → `auth_service.log_in` (case-insensitive username, `check_password_hash`) → `session["user_id"] = ...` → signed `HttpOnly; SameSite=Lax` cookie → `{"user": {...}}`. On load `AuthProvider` calls `GET /api/auth/session`; `RequireAuth` sends logged-out visitors to `/login`.

**Invite:** Match card **Invite** → `POST /api/invites {recipient_id, message?}` → `invite_service.send_invite` (must have liked them; one invite per pair either way) → row in `invites`. The recipient's `InboxPage` polls `GET /api/invites/inbox` every 5 s (rows where they're recipient/sender) → Accept/Decline → `PATCH /api/invites/<id> {status}` (recipient only, once). The sender can `DELETE` while pending.

**Edit profile:** `EditProfilePage` loads `GET /me` → form state → `PATCH /me` with the full form → `validate_update` cleans/validates → links/projects replaced → commit → returns updated profile.

## Identity (who is "me")
Login: `POST /api/auth/login` checks the password hash (`werkzeug.security`) and stores the user id in Flask's signed session cookie. Every "me" route calls `auth_service.current_profile_or_401()`, so "me" always comes from the server-signed cookie; the frontend never sends a user id for "me". Frontend: `AuthProvider` (`hooks/useAuth.tsx`) asks `GET /api/auth/session` on load, `RequireAuth` sends logged-out visitors to `/login`, and any `401` from the API logs the app out.

## Frontend structure
- `pages/` — route-level components (Login, Discover, Match, Inbox, Profile, EditProfile, Settings, NotFound)
- `hooks/useAuth.tsx` — `AuthProvider` + `useAuth()`: the logged-in user, `logIn`, `logOut`. Re-checks the session when the tab gets focus (all tabs share one cookie)
- `components/layout/` — `RequireAuth` (redirects to `/login`; remounts pages when the user changes), `AppLayout` (outlet + `BottomNav` with the inbox badge), `Navbar` (logo + slot + `PingIndicator` + `@username` / log out)
- `components/match/` — `MatchCard`; `components/invites/` — `InviteControl` (the Invite button / status on a match card)
- `components/profiles/` — `ProfileCard`, `ProfileHeader`, `SkillBadge`, `ProjectCard`, `Avatar`
- `components/discover/` — `SearchBar`, `FilterBar`
- `components/forms/` — `TagInput`
- `components/common/` — loading / error / empty states
- `services/api.ts` — the only place that calls `fetch`; sends the login cookie; throws `ApiError` with `status` and `fields`; a `401` fires `LOGGED_OUT_EVENT` so the app shows the login page
- `types/` — `profile.ts`, `invite.ts`, `auth.ts`: mirror the API's JSON
