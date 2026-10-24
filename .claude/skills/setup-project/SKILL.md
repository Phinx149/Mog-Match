---
name: setup-project
description: Scaffold the MogMatch C# Blazor solution from scratch, or get a new developer's local .NET environment running. Use when the repo has no MogMatch.sln yet, or when someone says "set up", "I just cloned", "dotnet run doesn't work", or "how do I start".
---

# Setup Project

## A. Solution not scaffolded yet (no `MogMatch.sln`)

Run from the repo root. Keep existing `README.md`, `CLAUDE.md`, `docs/`, `.claude/`.

1. Create the solution and projects:
   ```bash
   dotnet new gitignore
   dotnet new sln -n MogMatch
   dotnet new blazor -n MogMatch.Web -o src/MogMatch.Web --interactivity Server --auth Individual --use-program-main false
   dotnet new classlib -n MogMatch.Core -o src/MogMatch.Core
   dotnet new xunit -n MogMatch.Core.Tests -o tests/MogMatch.Core.Tests
   dotnet sln add src/MogMatch.Web src/MogMatch.Core tests/MogMatch.Core.Tests
   dotnet add src/MogMatch.Web reference src/MogMatch.Core
   dotnet add tests/MogMatch.Core.Tests reference src/MogMatch.Core
   ```
   `--auth Individual` gives ASP.NET Core Identity + EF Core + SQLite out of the box.
2. Add packages to the web project:
   ```bash
   cd src/MogMatch.Web
   dotnet add package AspNet.Security.OAuth.GitHub
   dotnet add package Microsoft.AspNetCore.SignalR.Client
   dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
   dotnet tool install --global dotnet-ef
   dotnet user-secrets init
   ```
3. In `Program.cs`:
   - Register GitHub login: `builder.Services.AddAuthentication().AddGitHub(o => { o.ClientId = builder.Configuration["Authentication:GitHub:ClientId"]!; o.ClientSecret = builder.Configuration["Authentication:GitHub:ClientSecret"]!; o.Scope.Add("read:user"); });`
   - Switch to a context factory: `builder.Services.AddDbContextFactory<AppDbContext>(...)` (keep Identity working with `AddEntityFrameworkStores<AppDbContext>()`).
   - `builder.Services.AddSignalR();` and `app.MapHub<ChatHub>("/hubs/chat");`
   - `builder.Services.AddHttpClient<GitHubStatsService>();`
4. Rename the template's `ApplicationDbContext` → `AppDbContext`, `ApplicationUser` → `AppUser`, and create the folders from `docs/ARCHITECTURE.md#solution-structure`.
5. Delete the template's demo pages (`Counter.razor`, `Weather.razor`) and the `Class1.cs` / `UnitTest1.cs` placeholders.
6. Add the entities from `docs/ARCHITECTURE.md` and create the first migration (use the `db-migration` skill).
7. Verify: `dotnet build` (0 errors), `dotnet test`, `dotnet watch --project src/MogMatch.Web`, then commit on branch `chore/scaffold`.

## B. New developer, solution already exists

Walk them through, checking each step's output before moving on:
1. `dotnet --version` → must start with `10.`. If not, install the .NET 10 SDK from https://dotnet.microsoft.com/download.
2. `dotnet tool install --global dotnet-ef` (or `update` if already installed).
3. `dotnet dev-certs https --trust`
4. `dotnet restore`
5. Set User Secrets (values from a teammate — never paste secrets into chat or commit them):
   ```bash
   cd src/MogMatch.Web
   dotnet user-secrets set "Authentication:GitHub:ClientId" "<id>"
   dotnet user-secrets set "Authentication:GitHub:ClientSecret" "<secret>"
   ```
6. `dotnet ef database update --project src/MogMatch.Web`
7. `dotnet watch --project src/MogMatch.Web` → open the URL it prints.
8. Have them make a tiny PR (add their name to `docs/ROADMAP.md` Team table) to practice the git flow in `CONTRIBUTING.md`.

## Common errors
| Error | Fix |
|---|---|
| `Could not execute because the specified command or file was not found` (dotnet ef) | `dotnet tool install --global dotnet-ef`, then open a new terminal |
| `NETSDK1045: The current .NET SDK does not support targeting .NET 10.0` | install the .NET 10 SDK |
| Browser says certificate not trusted | `dotnet dev-certs https --clean` then `--trust` |
| `SQLite Error 1: 'no such table'` | run `dotnet ef database update` |
| GitHub login `redirect_uri mismatch` | OAuth app callback must be `https://localhost:<port>/signin-github` matching `launchSettings.json` |
| Port already in use | change `applicationUrl` in `Properties/launchSettings.json` |
