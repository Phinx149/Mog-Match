# Architecture

## Overview
```
 Browser ── React SPA (Vite, :5173)
              │  fetch JSON  (src/services/api.ts, VITE_API_URL)
              ▼
 Flask API (:5001)  app factory in backend/app/__init__.py
   ├─ routes/      thin HTTP layer (health, profiles)
   ├─ services/    validation, filtering, serialization
   ├─ models/      SQLAlchemy models
   └─ seed.py      `flask seed` CLI
              │  SQLAlchemy ORM
              ▼
 SQLite (backend/instance/mogmatch.db)  ── or PostgreSQL via DATABASE_URL
```

Monorepo, two processes in dev. CORS on `/api/*` allows the Vite origin(s) from `CORS_ORIGINS`.

## Data model

```
users ──1:1── profiles ──1:N── profile_links
                     └──1:N── projects
```

| Table | Columns |
|---|---|
| `users` | `id` UUID PK, `email` unique nullable, `created_at`, `updated_at` |
| `profiles` | `id` UUID PK, `user_id` FK→users (unique, cascade), `full_name`, `username` unique, `avatar_url`, `location`, `education`, `bio`, `favorite_ide`, `experience_level`, JSON lists: `skills`, `interests`, `favorite_ai_agents`, `looking_for`, JSON `theme` (nullable; cosmetic card options, currently `{"background": "#rrggbb", "effect": "matrix" | "dvd" | "emoji" | "slogans" | "market" | "money" | "snow", "effect_options": {"brightness", "size", "speed", "glow", "count", "color_change", "color", "rain_color", "rain_rainbow", "rain_symbols", "emojis", "emoji_count", "emoji_angle", "emoji_path", "emoji_spin", "slogans", "slogan_color", "slogan_style", "slogan_tilt", "slogan_alternate", "chart_volatility", "chart_mood", "chart_palette", "chart_ticker", "chart_label", "money_kind", "money_count", "money_wind", "money_weight", "snow_kind", "snow_count", "snow_wind"}}`), timestamps |
| `profile_links` | `id` UUID PK, `profile_id` FK (cascade), `label`, `url`, `position` |
| `projects` | `id` UUID PK, `profile_id` FK (cascade), `title`, `description`, `project_url`, JSON `technologies`, `position`, timestamps |

The original hand-drawn schema (`id, users_id, loc, langs, fav_ide, fav_agents`) maps to `profiles.id`, `profiles.user_id`, `location`, `skills` (languages are skills), `favorite_ide`, `favorite_ai_agents`.

**Portability:** `db.Uuid` → native `uuid` on Postgres, `CHAR(32)` on SQLite. `db.JSON` → `json` on Postgres. No SQLite-only SQL anywhere.

### Planned tables (later milestones)
```
swipes   (swiper_id → profiles, target_id → profiles, action like|pass, created_at)  PK (swiper_id, target_id)
matches  (id, profile_a_id, profile_b_id, created_at, intersect_summary JSON)       unique pair
messages (id, match_id → matches, sender_id → profiles, body, created_at)
```

## Request flow examples

**Discover:** `DiscoverPage` → debounced `listProfiles({q, skills})` → `GET /api/profiles?q=..&skills=..` → `profile_service.list_profiles` (filters in Python, excludes demo profile) → `{profiles, count}`. Like/Pass recorded in React state only.

**Edit profile:** `EditProfilePage` loads `GET /me` → form state → `PATCH /me` with the full form → `validate_update` cleans/validates → links/projects replaced → commit → returns updated profile.

## Identity (for now)
No auth. The backend reads `DEMO_USER_EMAIL` from config and treats that user as "me". The frontend never sends a user id for "me". When auth arrives, `get_demo_profile()` is replaced by "profile of the logged-in user" — routes don't change.

## Frontend structure
- `pages/` — route-level components (Discover, Profile, EditProfile, Settings, NotFound)
- `components/layout/` — `AppLayout` (outlet + `BottomNav`), `Navbar` (logo + slot + `PingIndicator`)
- `components/profiles/` — `ProfileCard`, `ProfileHeader`, `SkillBadge`, `ProjectCard`, `Avatar`, `ThemeScope` (applies a profile's theme to everything inside it), `ThemePicker` (background color and effect picker on Edit Profile; each effect's presets and tuning sit in a collapsible menu under it), `EmojiPicker` and `SloganPicker` (the list editors inside it), `MatrixRain`, `BouncingDvd`, `FloatingEmoji`, `ScrollingSlogans`, `VolatileMarket`, `FallingMoney` and `FallingSnow` (the `matrix`, `dvd`, `emoji`, `slogans`, `market`, `money` and `snow` effects: canvas animations; the logo's bounce rules live in `utils/dvdMotion.ts`, the emoji's movement in `utils/emojiMotion.ts`, the slogan rows' layout in `utils/sloganMarquee.ts` the made-up price simulation in `utils/marketSim.ts` the falling cash's wind, flutter and tumble in `utils/moneyMotion.ts` and the snowflakes' fall, sway and wind in `utils/snowMotion.ts`)
- `components/discover/` — `SearchBar`, `FilterBar`
- `components/forms/` — `TagInput`
- `components/common/` — loading / error / empty states
- `services/api.ts` — the only place that calls `fetch`; throws `ApiError` with `status` and `fields`
- `types/profile.ts` — mirrors the API's JSON
