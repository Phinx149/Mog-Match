---
name: git-help
description: Help a beginner with git and GitHub in this repo — branching, committing, pushing, opening PRs, pulling main, resolving merge conflicts, undoing mistakes. Use when someone says "git", "merge conflict", "I committed to main", "how do I make a PR", "push rejected", or "undo".
---

# Git Help

Workflow rules are in `CONTRIBUTING.md#3-git-workflow`. Always run `git status` first and explain what it shows before changing anything. Prefer safe, reversible commands; **confirm before anything that discards work** (`reset --hard`, `checkout -- .`, `push --force`).

## Everyday loop
```bash
git checkout main && git pull
git checkout -b feat/<name>
# edit
git status
git add -A
git commit -m "feat: <what>"
git push -u origin feat/<name>
gh pr create --fill
```

## Common situations

**"I committed to main by accident" (not pushed yet)**
```bash
git branch feat/my-work          # save the commits on a new branch
git reset --keep origin/main     # move main back (keeps working-tree changes safe)
git checkout feat/my-work
```

**"Push rejected — fetch first"** → someone pushed to your branch. `git pull --rebase`, then push.

**"My branch is behind main"**
```bash
git checkout main && git pull
git checkout feat/<name>
git merge main                   # simpler than rebase for beginners
```

**Merge conflict**
1. `git status` lists files marked "both modified".
2. In each file, find `<<<<<<<`, `=======`, `>>>>>>>`. Keep the correct code (often a bit of both), delete the markers.
3. Conflict in `Data/Migrations/AppDbContextModelSnapshot.cs`? Don't hand-merge it — take main's version, remove your migration, re-add it (see `db-migration` skill).
4. `dotnet build` to make sure it compiles, then `git add <file>` and `git commit`.

**Undo the last commit but keep the changes** → `git reset --soft HEAD~1`

**Throw away changes to one file** → `git restore <file>` (confirm first — this is permanent)

**Accidentally committed a secret** → tell the team immediately and **rotate the secret** (e.g. regenerate the GitHub OAuth client secret). Removing it from history isn't enough once it's pushed.

## Never commit
`bin/`, `obj/`, `*.db`, `.vs/`, `appsettings.Development.json` with secrets — the `.gitignore` from `dotnet new gitignore` covers most of these; add `*.db` if missing.
