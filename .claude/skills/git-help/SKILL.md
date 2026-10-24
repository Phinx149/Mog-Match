---
name: git-help
description: Help a beginner with git and GitHub in this repo — branching off dev, committing, pushing, opening PRs, syncing with dev, resolving merge conflicts, undoing mistakes. Use when someone says "git", "merge conflict", "I committed to main", "how do I make a PR", "push rejected", or "undo".
---

# Git Help

Workflow rules: `CONTRIBUTING.md#3-git-workflow`. `main` = demo-ready, `dev` = integration, feature branches come off `dev`.

Always run `git status` first and explain what it shows before changing anything. Prefer safe, reversible commands. **Confirm before anything that discards work** (`reset --hard`, `restore`, `clean`, `push --force`).

## Everyday loop
```bash
git checkout dev && git pull
git checkout -b feat/<name>
# edit
git status
git add -A
git commit -m "feat: <what>"
git push -u origin feat/<name>
gh pr create --base dev --fill
```

## Common situations

**Committed to `dev` or `main` by accident (not pushed yet)**
```bash
git branch feat/my-work              # save the commits on a new branch
git reset --keep origin/<dev|main>   # move the branch back (refuses if it would lose uncommitted work)
git checkout feat/my-work
```

**"Push rejected — fetch first"**: someone else pushed to your branch. Run `git pull --rebase`, then push.

**Branch is behind `dev`**
```bash
git checkout dev && git pull
git checkout feat/<name>
git merge dev                        # simpler than rebase for beginners
```

**Merge conflict**
1. `git status` lists files marked "both modified".
2. In each file, find `<<<<<<<`, `=======`, `>>>>>>>`. Keep the correct code (often a bit of both) and delete the markers.
3. `package-lock.json` conflict: take `dev`'s version (`git checkout --theirs package-lock.json` during a merge), then run `npm install` and commit the result.
4. Two Alembic migrations with the same parent after merging: see the `db-migration` skill (`flask db merge heads`).
5. Run `pytest` / `npm run build`, then `git add <file>` and `git commit`.

**Undo the last commit but keep the changes**: `git reset --soft HEAD~1`

**Throw away changes to one file**: `git restore <file>`. Confirm first, because this is permanent.

**Committed a secret** (`.env`, API key): tell the team right away and **rotate the secret**. Removing it from history isn't enough once it has been pushed.

## Never commit
`.env`, `.env.local`, `*.db` / `backend/instance/`, `.venv/`, `node_modules/`, `dist/`. The root `.gitignore` already covers these. If one shows up in `git status`, check that the `.gitignore` is still there before committing anything.
