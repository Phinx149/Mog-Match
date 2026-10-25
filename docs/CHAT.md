# Inbox chat and Project studio

Send a **Match request** from Match. The recipient opens Inbox → Requests and chooses
**Accept & chat**. Either participant can then open the same persistent conversation from
Inbox → Messages or the **Open chat** button on their match card. Declining or cancelling
a pending request does not open a conversation. Existing accepted requests work immediately.

## Run locally

After pulling the feature, from `backend/`:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m flask --app run db upgrade
.venv/Scripts/python.exe run.py
```

Start the backend with `python run.py` so `socketio.run()` serves the WebSocket endpoint.
Restart an already running backend after installing dependencies. From `frontend/`, run
`npm install` and `npm run dev` as usual. Use the same hostname for both servers
(`localhost` on both, or `127.0.0.1` on both) so the login cookie is sent consistently.

For two-person testing, run `flask seed-test-users`, then use separate browser profiles or
a normal window and an incognito window. Accounts: `user1` / `123`, `user2` / `234`.
They like each other already; send and accept a request to start chatting.

## Project studio

Set these in **backend/.env** and restart the backend:

```dotenv
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4.1-mini
```

The key never goes to the browser. A funded OpenAI API account with access to the configured
model is required. An exhausted balance, missing key, provider failure, or refused generation
produces an error; no placeholder plan is saved as if it came from the model.

Open Project studio inside a conversation and optionally describe scope or constraints.
On wide screens, drag its left divider to resize the panel. Focus the divider and use the
arrow keys for keyboard resizing; Home/End select the minimum/maximum width and a double-click
restores the default. The width is remembered in your browser while the chat retains room for
its composer. On small screens the studio uses the full conversation area.

Once a plan exists, **Download design doc** stays at the top of the studio. It downloads the
selected version as Markdown (`project-title-vN.md`), including architecture, tech stack,
responsibilities and build plan.

Generation uses both profiles' skills, experience, interests, goals and bios, the original
match request, the previous plan (if any), and up to 100 recent messages bounded to 24,000
characters, prioritizing recent discussion. This context is sent to OpenAI only when a
participant clicks Generate. Requests use `store=False`.

The structured result includes the idea, audience, problem, MVP features, discussion decisions,
architecture/data flow, justified technology stack, data model, API contracts, responsibilities
and learning goals for both participants, ordered milestones/estimates, testing, deployment,
risks and open questions. Each successful generation creates a version visible to both users
in real time and downloadable as a Markdown design document. New-idea generation has a
30-second cooldown. All AI requests in a conversation share one in-flight-request lock.

The integration follows the [OpenAI Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

## Ask AI about a selected document

Select a plan version and open **Ask AI** in Project studio. The selection stays pinned when
a teammate publishes another version, so discussing version 1 never silently changes to version 2.

- **Ask a question** explains the selected document without creating or modifying a plan.
- **Propose changes** returns a revision preview with a change summary, expandable Before/Proposed
  comparisons for each changed section, and the full revised document.
- **Save as new version** saves that exact preview, records its source version, and shares the
  new document with both participants. It makes no additional OpenAI request. The source is
  preserved, including when the proposal was based on an older version.

Questions, answers and previews are shared with the teammate and persisted separately for each
plan version. Both participants can save a shared preview; simultaneous or repeated saves create
only one version. The current AI discussion is restored after reopening the tab or reconnecting.
Older discussion can be loaded 30 turns at a time. A five-second conversation-wide AI cooldown
and client request tokens limit accidental repeated requests and duplicate billing.

Assistant context includes the selected document, both profiles, the bounded recent teammate
chat, and up to 20 recent studio turns for that version (12,000 question/answer characters).
Only a successful AI response is saved. Provider errors leave the request draft and existing
document intact. Use Enter to send, Shift+Enter for a new line.

## Persistence, access and realtime events

- The accepted invite ID identifies a conversation. Every read, send, read-marker and generation
  verifies accepted status and participant membership. Other people's IDs return 404.
- `chat_messages` stores message bodies, sender, timestamp and a client UUID. A database unique
  constraint makes retries idempotent. Messages are limited to 2,000 characters.
- `project_ideas` stores shared, versioned design documents and the last message used as context.
- `studio_turns` stores each question/answer pair, optional revision preview, requester, and the
  saved version ID after Apply. `project_ideas.parent_idea_id` records revision lineage.
- `invites` stores each participant's read cursor. Cursors only advance; unread counts exclude
  messages sent by the current user. The navigation badge includes unread messages and requests.
- Socket connections use the existing signed login cookie and join a server-selected profile
  room. Clients cannot choose another user's room. Logout/account switch disconnects old sockets.
- Client event: `chat:send` with `{conversation_id, body, client_token}`. The acknowledgement
  returns `{message}` on success or `{error, status}` on failure. Save occurs before broadcast.
- Server events: `chat:message`, `chat:idea`, `chat:studio`, `chat:read`, `inbox:updated`. Delivery is restricted
  to participant rooms. Reconnect fetches persisted history to recover missed events.
- HTTP: `GET /api/conversations`, `GET /:id/messages?before=<message-id>` (50 per page),
  `POST /:id/read`, and `GET/POST /:id/ideas`, all under `/api/conversations`.
- Version-scoped AI: `GET/POST /:id/ideas/:idea_id/assistant`; Apply a preview with
  `POST /:id/ideas/:idea_id/assistant/:turn_id/apply`. The same membership/accepted-status
  checks apply to every endpoint. A plan or turn ID from another conversation returns 404.

The implementation uses [Flask-SocketIO's authenticated session and room support](https://flask-socketio.readthedocs.io/en/latest/implementation_notes.html).
The current deployment target is a **single backend process**, with threading and
`simple-websocket`. Multiple backend workers need a shared Socket.IO message queue and a
distributed generation lock before scaling beyond that configuration.

## Verification

From `backend/`: `.venv/Scripts/python.exe -m pytest -q`.

From `frontend/`: `npm run build` and `npm run test:e2e`.

The browser test starts an isolated temporary database/backend on port 5002 and a Vite server
on 5174. It uses separate browser sessions and a stub provider, so it neither edits your database
nor spends OpenAI credits. It covers request acceptance, real WebSocket message delivery in
both directions, persistence after reload, shared plans, version-scoped AI explanations,
revision previews, original-version preservation, shared Apply updates, downloads and mobile layout. It saves
desktop/mobile screenshots in ignored `frontend/test-results/`. The default browser is installed
Edge; set `E2E_BROWSER_CHANNEL=chrome` for Chrome or adjust the Playwright project for your OS.
