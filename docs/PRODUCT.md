# Product Spec

## Elevator pitch
A dating app, but for developers. Find a hackathon partner, co-builder or study buddy whose skills *complement* yours — and let the **Intersect Engine** suggest what you should build together.

Hackathon theme: **Connect & Intersect** — connect people, then explore what happens where their skills and interests overlap.

## Personas
- **Hackathon Hopper** – needs a teammate with the skills they lack, fast.
- **Side-Project Builder** – has an idea, wants a co-builder.
- **Learner** – wants a mentor or study partner on a specific stack.

## Features

### 1. Tech Profile ✅ (milestone 1)
Large circular avatar · Edit Profile button · full name + username · location · education · external links · About · technical skills · projects · interests. Also: favorite IDE, favorite AI coding agents, experience level, "looking for". Vertically scrollable.

### 2. Discover ✅ (milestone 1)
- Top bar: search, refresh, API ping indicator.
- Filters dropdown + removable skill chips (e.g. Rust, Frontend).
- Vertical list of developer cards: avatar, basic info, skill tags, **Pass** (left) / **Like** (right).
- Bottom nav: Discover · Profile · Settings.
- Milestone 1: likes/passes live in React state only.

### 3. Matching (milestone 2)
- Persistent swipes; mutual like → **Match** 🎉.
- Matches list.

### 4. Intersect Engine (milestone 3 — our differentiator)
For a pair of developers:
- **Overlap** — shared skills/interests ("you both know Rust and like games").
- **Complement** — skills only one of you has ("Maya brings Frontend, you bring Backend").
- **Project ideas** — 2–3 concrete things you could build together, generated from the above.

### 5. Stretch
- **Mog Score** – playful 0–1000 profile score + team score (see `MOG_SCORE.md`).
- Real-time chat between matches, voice calls.
- GitHub sign-in.

## Screens
| Route | Screen | Status |
|---|---|---|
| `/discover` | Discover list | ✅ |
| `/profile` | My profile | ✅ |
| `/profile/edit` | Edit my profile | ✅ |
| `/profile/:id` | Someone else's profile | ✅ |
| `/settings` | Settings (placeholder) | ✅ |
| `/matches` | Matches + Intersect panel | later |

## Demo flow
```
Discover → search/filter → open a profile → Like
   → (M2) Match! → (M3) Intersect ideas → edit my profile → refresh → still saved
```

## Safety
- Keep the "dating" framing playful — this is professional/creative matchmaking.
- Later: block + report on profiles and chats; never display private email.
