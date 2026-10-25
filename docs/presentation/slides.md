---
marp: true
paginate: true
---

<!-- Present with Marp: VS Code "Marp for VS Code" extension (Open Preview / Export), or
     `npx @marp-team/marp-cli docs/presentation/slides.md --pdf --allow-local-files`.
     Speaker notes are the HTML comments under each slide. Total talk time: about 1 minute. -->

<style>
section { background: #0b0d17; color: #e8eaf6; font-size: 26px; padding: 40px 32px; }
h1, h2 { color: #a78bfa; }
h2 { font-size: 42px; margin-bottom: 0.6em; }
strong { color: #67e8f9; }
a { color: #67e8f9; }
section.lead { text-align: center; padding: 60px; font-size: 30px; }
section.lead h1 { font-size: 80px; }
li { margin-bottom: 0.5em; }
section.arch p { text-align: center; margin: 0.2em 0; }
section.arch p:last-of-type { font-size: 22px; color: #9aa0bd; }
section.arch code { color: #67e8f9; background: none; }
</style>

<!-- _class: lead -->

# mogmatch 💜

### Tinder for developers.
Find a teammate whose skills **complement** yours, then build something together.

*Hackathon theme: Connect & Intersect*

<!-- (~6s) MogMatch is matchmaking for developers: find a teammate whose skills complement yours, then build something together. -->

---

## 🔎 Discover

- Search + filter by **skill, goal, tier**
- **Mog Score** badge on every card
- **Like** or **Pass**

![bg right:68% fit](img/discover.png)

<!-- (~8s) Discover lets you search and filter developers by skill, goal and tier. Every card shows a Mog Score. -->

---

## 👑 Mog Score

- **0–100** profile rating
- Weird languages win: **COBOL beats Python**
- 🥚 Hello World → 👑 Gigamogger
- Animated profile themes

![bg right:68% fit](img/mog-score.png)

<!-- (~10s) Every profile gets a Mog Score out of a hundred, and obscure languages score highest. Gigamoggers even get animated themes. -->

---

## 💘 Mog Match

- Likes **ranked by similarity**
- Shows *why*: skills, interests, goals
- One tap to send a **match request**

![bg right:68% fit](img/mog-match.png)

<!-- (~8s) Liked profiles are ranked by how much you overlap, with the exact reasons. Then you send a match request. -->

---

## 🔥 Team Mog Score

- Accept a request, both get a **reveal**
- Scored out of **1000**
- Rewards *complementary* skills, not clones

![bg right:68% fit](img/team-mog-score.png)

<!-- (~10s) When a request is accepted, you both get a Team Mog Score out of a thousand. It rewards complementary skills, and shows why. -->

---

## 💬 Chat + Studio

- **Real-time chat**
- **Project Studio**: AI drafts a shared **project plan** from your chat and both profiles
- Versioned, **downloadable**

![bg right:68% fit](img/chat-studio.png)

<!-- (~10s) Then chat live. Project Studio uses both profiles and your conversation to draft a shared project plan you can download. -->

---

<!-- _class: arch -->

## 🧱 Under the hood

![w:1216](img/architecture.svg)

One domain, one signed cookie: Vercel sends `/api/*` and `/socket.io/*` to Flask, everything else to the static React app.

<!-- (~10s) Vercel serves the React app and routes API and WebSocket traffic to one Flask app. Postgres stores everything, and OpenAI is only ever called server-side. -->

---

<!-- _class: lead -->

## Next: the Intersect Engine 🧩

Project ideas generated from where two developers' skills *intersect*.

# Thanks! 💜

<!-- (~5s) Next up is the Intersect Engine. Thanks! -->
