---
name: new-feature
description: Build a new Blazor page, component, or service in MogMatch following project conventions, from branch to PR. Use when a developer wants to add a feature, screen, button, form, or service (e.g. "add the onboarding form", "make a profile card", "build the discover page").
---

# New Feature

Guide the developer through these steps. Explain briefly *why* at each step — many teammates are beginners.

## 1. Branch
```bash
git checkout main && git pull
git checkout -b feat/<short-name>
```

## 2. Decide where code goes
| Building… | Location |
|---|---|
| A page (has a URL) | `src/MogMatch.Web/Components/Pages/Name.razor` with `@page "/route"` |
| Reusable UI piece | `src/MogMatch.Web/Components/Shared/Name.razor` |
| DB / HTTP work | a service in `src/MogMatch.Web/Services/`, registered in `Program.cs` |
| Pure logic (scoring, ranking, formatting) | `src/MogMatch.Core/...` + xUnit test in `tests/MogMatch.Core.Tests/` |
| Real-time stuff | `Hubs/ChatHub.cs` (see `realtime-chat` skill) |
| Schema change | `db-migration` skill |

Check `docs/PRODUCT.md` for expected behavior and `docs/ARCHITECTURE.md` for the data model.

## 3. Patterns

**Service (does the DB work)**
```csharp
public class ProfileService(IDbContextFactory<AppDbContext> dbFactory)
{
    public async Task<Profile?> GetByUserIdAsync(string userId)
    {
        await using var db = await dbFactory.CreateDbContextAsync();
        return await db.Profiles.Include(p => p.Skills)
                                .AsNoTracking()
                                .FirstOrDefaultAsync(p => p.UserId == userId);
    }
}
// Program.cs
builder.Services.AddScoped<ProfileService>();
```

**Page that uses it**
```razor
@page "/profile/me"
@attribute [Authorize]
@inject ProfileService Profiles
@inject AuthenticationStateProvider Auth

@if (profile is null) { <p>Loading…</p> }
else
{
    <h1>@profile.DisplayName</h1>
    <MogBadge Score="profile.MogScore" />
}

@code {
    private Profile? profile;

    protected override async Task OnInitializedAsync()
    {
        var user = (await Auth.GetAuthenticationStateAsync()).User;
        var userId = user.FindFirstValue(ClaimTypes.NameIdentifier)!;
        profile = await Profiles.GetByUserIdAsync(userId);
    }
}
```

**Reusable component with a parameter + event**
```razor
@* Components/Shared/ProfileCard.razor *@
<div class="card p-3">
    <h5>@Profile.DisplayName</h5>
    <button class="btn btn-success" @onclick="() => OnLike.InvokeAsync(Profile.Id)">❤️</button>
</div>

@code {
    [Parameter, EditorRequired] public Profile Profile { get; set; } = default!;
    [Parameter] public EventCallback<Guid> OnLike { get; set; }
}
```

**Forms:** use `<EditForm Model="model" OnValidSubmit="SaveAsync">` with `<DataAnnotationsValidator />` and `[Required]`, `[StringLength(80)]` on the model.

Rules:
- Get the current user from `AuthenticationStateProvider` on the server — never from a query string or hidden field.
- Use `IDbContextFactory` + `await using` (one short context per operation). Don't inject `AppDbContext` directly into components.
- Pages that need login get `@attribute [Authorize]`.
- Handle loading (`null` check) and empty states.
- Add `@using` lines to `Components/_Imports.razor` instead of repeating them.

## 4. Verify
```bash
dotnet build && dotnet test
dotnet watch --project src/MogMatch.Web
```
Click through the feature. Check the terminal for exceptions.

## 5. Commit + PR
```bash
dotnet format
git add -A
git commit -m "feat: <what it does>"
git push -u origin feat/<short-name>
gh pr create --fill   # or open the PR on GitHub
```
PR description: what changed, screenshot if UI, how to test.
