# Product Spec

## Elevator pitch
Tinder for devs. Find a hackathon partner, co-founder, or study buddy whose skills *complement* yours — and flex your Mog Score while you're at it.

## Personas
- **Hackathon Hopper** – needs a teammate with the skills they lack, fast.
- **Side-Project Builder** – has an idea, wants a co-builder.
- **Learner** – wants a mentor or study partner on a specific stack.

## Core features

### 1. Tech Profile
Fields:
- Display name, avatar (from GitHub), headline (≤ 80 chars)
- Bio / description (free text, ≤ 1000 chars) — feeds the Mog Score
- Skills: list of `{ name, level: 1–5 }` (e.g. React 4, Python 3)
- Role tags: frontend · backend · fullstack · mobile · ML/AI · design · devops · data · game dev
- Experience: years coding, # hackathons
- Links: GitHub (required via OAuth), LinkedIn, portfolio
- Looking for: hackathon team · side project · mentor · mentee · just vibes

### 2. Mog Score
- 0–1000, shown as a number + tier badge (see `MOG_SCORE.md`).
- Recomputed on profile save and nightly (GitHub stats change).
- Breakdown visible on your own profile ("+120 from skill depth") so users know how to improve.

### 3. Discover / Recommendations
- Card stack of recommended profiles. Each card: avatar, headline, top 5 skills, Mog tier, **predicted Team Mog Score** with you.
- Actions: ❤️ Like · ✖️ Pass · ⭐ Super-like (1/day).
- Filters: role, looking-for, skill.
- Mutual like → **Match** 🎉.

### 4. Team Mog Score
- Shown on every match and in chat header.
- Rewards complementary roles + shared interests (see `MOG_SCORE.md`).
- Stretch: groups of 3–4 (a "squad") with a squad score.

### 5. Chat
- 1:1 real-time text chat per match (SignalR `ChatHub`).
- Typing indicator, read receipts (stretch), code-block formatting with ``` (stretch).
- Unmatch / block / report.

### 6. Voice chat
- "Start call" button in chat → peer-to-peer WebRTC audio call, signaled over SignalR.
- Mute, leave. Stretch: screen share.

## User flow
```
Landing → Sign in with GitHub → Build profile → See Mog Score reveal
   → Discover (swipe) → Match! → Chat → Voice call
```

## Screens
1. `/` Landing
2. `/onboarding` Profile builder (multi-step)
3. `/profile/[id]` Profile view (own profile shows score breakdown)
4. `/discover` Swipe stack
5. `/matches` Match list with team scores
6. `/chat/[matchId]` Chat + call button
7. `/leaderboard` (stretch) Top Mog Scores / top teams

## MVP scope (must ship for demo)
- [ ] GitHub login
- [ ] Profile create/edit
- [ ] Individual Mog Score with breakdown
- [ ] Discover + like/pass + matching
- [ ] Team Mog Score on matches
- [ ] Real-time text chat

**Stretch:** voice chat · leaderboard · squads · LLM-based bio analysis · notifications.

## Safety
- Block + report on every profile and chat.
- No private info beyond what users enter; GitHub email is never displayed.
- Keep the "dating" framing playful — this is for professional/creative matching.
