# Contributing

Welcome! This guide assumes you're new — skim it once, then keep it open.

## 1. Tools you need

| Tool | Version | Check |
|---|---|---|
| Python | 3.12+ | `python --version` (Windows: `py --version`) |
| Node.js + npm | Node 20.19+ / 22+ | `node -v`, `npm -v` |
| Git | any recent | `git --version` |
| Editor | VS Code recommended | extensions: Python, ESLint, Tailwind CSS IntelliSense |
| Claude Code (optional) | — | skills in `.claude/skills/` |

## 2. First-time setup

Follow **Backend setup** and **Frontend setup** in the [developer guide](docs/ARCHITECTURE.md#backend-setup). Short version:

```bash
# terminal 1
cd backend && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt && cp .env.example .env
flask db upgrade && flask seed && python run.py

# terminal 2
cd frontend && npm install && cp .env.example .env.local && npm run dev
```

## 3. Git workflow

- `main` = demo-ready. `dev` = integration branch. Feature branches come off `dev`.

```bash
git checkout dev && git pull
git checkout -b feat/discover-filters      # feat/, fix/, docs/, chore/
# ...code...
git add -A
git commit -m "feat: add interest filter"   # conventional commit style
git push -u origin feat/discover-filters
# open a PR into dev; one teammate reviews
```

Rules:
- Don't push directly to `main`.
- Keep PRs small (one feature/fix).
- CI (`.github/workflows/ci.yml`) runs `pytest`, the TypeScript check and the frontend build on every PR. Get it green before asking for review; to reproduce a failure locally, run `python -m pytest` in `backend/` and `npm run typecheck && npm run build` in `frontend/`.
- Pull `dev` into your branch often: `git pull origin dev`.
- Two people generated migrations at the same time? See the `db-migration` skill.
- Merge conflict? Keep the right code, delete the `<<<<<<<`/`=======`/`>>>>>>>` markers, re-run tests, commit.

**Commit prefixes:** `feat:` · `fix:` · `docs:` · `style:` · `refactor:` · `test:` · `chore:`

## 4. Code style

**Python**
- `snake_case` functions/variables, `PascalCase` classes, type hints on public functions.
- Routes stay thin — put logic in `app/services/`.
- Validate request data; return `{"error": {"message": ...}}` with the right status code.
- Add/extend a pytest test for every endpoint change.

**TypeScript / React**
- `PascalCase.tsx` components, one per file. Hooks start with `use`.
- No `any`. API types live in `src/types/`, API calls in `src/services/api.ts`.
- Style with Tailwind classes; use theme colors (`bg-surface`, `border-line`, `text-muted`) from `src/index.css`.
- Always handle loading, error and empty states.

Before pushing: `pytest` (backend) and `npm run build` (frontend).

## 5. Getting help

1. `docs/ARCHITECTURE.md` (setup, API, data model) and the rest of `docs/`.
2. Claude Code — skills in `.claude/skills/` know this project's conventions.
3. Team chat — paste the **full error**, the command you ran, and what you expected.
