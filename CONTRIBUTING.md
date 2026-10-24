# Contributing

Welcome! This guide assumes you're new — skim it once, then keep it open.

## 1. Tools you need

| Tool | Version | Check |
|---|---|---|
| .NET SDK | 10.x | `dotnet --version` |
| EF Core CLI | matches SDK | `dotnet tool install --global dotnet-ef` then `dotnet ef --version` |
| Git | any recent | `git --version` |
| IDE | Visual Studio 2022+ (ASP.NET workload), **or** VS Code + C# Dev Kit, **or** JetBrains Rider | — |
| Claude Code (optional) | — | `claude` — skills in `.claude/skills/` |

## 2. First-time setup

```bash
git clone https://github.com/Phinx149/social-coding-Hackathon.git
cd social-coding-Hackathon
dotnet restore
dotnet dev-certs https --trust                     # once per machine, for https://localhost
dotnet ef database update --project src/MogMatch.Web
dotnet watch --project src/MogMatch.Web
```

### Secrets
Secrets live in **.NET User Secrets**, never in `appsettings.json`:
```bash
cd src/MogMatch.Web
dotnet user-secrets set "Authentication:GitHub:ClientId" "<id>"
dotnet user-secrets set "Authentication:GitHub:ClientSecret" "<secret>"
dotnet user-secrets set "GitHub:Token" "<personal access token>"
```
Ask a teammate for the shared GitHub OAuth app values. **Never commit secrets.**

## 3. Git workflow

Short-lived feature branches and pull requests into `main`.

```bash
git checkout main && git pull           # always start fresh
git checkout -b feat/profile-form        # feat/, fix/, docs/, chore/
# ...code...
git add -A
git commit -m "feat: add profile form"   # conventional commit style
git push -u origin feat/profile-form
# open a PR on GitHub, ask one teammate to review
```

Rules:
- **Don't push directly to `main`.**
- Keep PRs small (one feature/fix).
- Pull `main` into your branch often: `git pull origin main`.
- **EF migrations conflict easily** — if two people add migrations at once, the second to merge re-creates theirs (see `db-migration` skill).
- Merge conflict? Open the file, keep the right parts, delete the `<<<<<<<`/`=======`/`>>>>>>>` markers, commit.

### Commit prefixes
`feat:` new feature · `fix:` bug fix · `docs:` docs only · `style:` formatting · `refactor:` no behavior change · `test:` tests · `chore:` tooling/deps

## 4. Code style

- Follow standard .NET naming: `PascalCase` for types, methods, properties, components; `camelCase` for locals/parameters; `_camelCase` for private fields; interfaces start with `I`.
- One class/record per file; file name = type name.
- Nullable reference types are **on** — don't silence warnings with `!` unless you're sure.
- Use `async`/`await` for DB and HTTP calls; method names end in `Async`.
- Business logic (scoring, matching) goes in **`MogMatch.Core`**, not in `.razor` files — so it can be tested.
- Inject services with `@inject` / constructor injection; don't `new` up services.
- Run `dotnet format` and `dotnet test` before pushing.

## 5. Where things go

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#solution-structure).

## 6. Getting help

1. Check the docs in `docs/`.
2. Ask Claude Code — the skills in `.claude/skills/` know this project's conventions.
3. Ask in the team chat. Paste the **full error message**, what you ran, and what you expected.
