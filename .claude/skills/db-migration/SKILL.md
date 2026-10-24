---
name: db-migration
description: Add or change EF Core entities, DbContext configuration, migrations, or seed data for MogMatch. Use when someone says "add a column", "new table", "migration", "no such table", "pending model changes", "seed fake profiles", or edits src/MogMatch.Web/Data/.
---

# Database Migration (EF Core)

Schema reference: `docs/ARCHITECTURE.md#data-model-ef-core-entities`. Files: `src/MogMatch.Web/Data/AppDbContext.cs`, `Data/Entities/`, `Data/Migrations/`.

## Workflow
1. Add/change the entity class in `Data/Entities/` (and a `DbSet<T>` in `AppDbContext` if it's new).
2. Configure keys/constraints in `OnModelCreating` (see below).
3. Create the migration:
   ```bash
   dotnet ef migrations add AddBioToProfile --project src/MogMatch.Web
   ```
   Name it in PascalCase describing the change.
4. **Open the generated file and read it** — make sure it does what you expect (no surprise `DropTable`).
5. Apply: `dotnet ef database update --project src/MogMatch.Web`
6. Commit the entity change **and** the migration files (including `AppDbContextModelSnapshot.cs`) together.

**Never edit or delete a migration that's already on `main`** — add a new one.

## OnModelCreating patterns for this app
```csharp
protected override void OnModelCreating(ModelBuilder b)
{
    base.OnModelCreating(b);   // required for Identity tables

    b.Entity<Profile>(e =>
    {
        e.HasIndex(p => p.UserId).IsUnique();
        e.Property(p => p.Headline).HasMaxLength(80);
        e.Property(p => p.Bio).HasMaxLength(1000);
        e.HasOne<AppUser>().WithOne(u => u.Profile).HasForeignKey<Profile>(p => p.UserId);
    });

    b.Entity<ProfileSkill>().HasKey(s => new { s.ProfileId, s.Name });           // composite key
    b.Entity<Swipe>().HasKey(s => new { s.SwiperId, s.TargetId });
    b.Entity<Swipe>().Property(s => s.Action).HasConversion<string>();           // store enum as text
    b.Entity<Match>().HasIndex(m => new { m.UserAId, m.UserBId }).IsUnique();
    b.Entity<Message>().Property(m => m.Body).HasMaxLength(4000);
    b.Entity<Message>().HasIndex(m => new { m.MatchId, m.CreatedAt });
    b.Entity<Block>().HasKey(x => new { x.BlockerId, x.BlockedId });
}
```

## Mutual-like → Match (in `MatchService`, not a DB trigger)
```csharp
public async Task<Match?> SwipeAsync(Guid me, Guid target, SwipeAction action)
{
    await using var db = await dbFactory.CreateDbContextAsync();
    await using var tx = await db.Database.BeginTransactionAsync();

    db.Swipes.Add(new Swipe { SwiperId = me, TargetId = target, Action = action, CreatedAt = DateTime.UtcNow });

    Match? match = null;
    var theyLikedMe = action != SwipeAction.Pass && await db.Swipes.AnyAsync(s =>
        s.SwiperId == target && s.TargetId == me && s.Action != SwipeAction.Pass);

    if (theyLikedMe)
    {
        var (a, b) = me.CompareTo(target) < 0 ? (me, target) : (target, me);   // ordered pair
        match = new Match { UserAId = a, UserBId = b, CreatedAt = DateTime.UtcNow /* + TeamScore */ };
        db.Matches.Add(match);
    }

    await db.SaveChangesAsync();
    await tx.CommitAsync();
    return match;
}
```

## Seed data
Create `Data/DbSeeder.cs` with 15–20 varied profiles (different roles/skills so team scores look interesting). Call it from `Program.cs` only when `app.Environment.IsDevelopment()` and the Profiles table is empty.

## SQLite vs PostgreSQL
- Dev uses SQLite (`Data Source=mogmatch.db`, file is git-ignored). Prod uses PostgreSQL via `UseNpgsql` when the connection string isn't SQLite.
- Avoid provider-specific SQL in migrations. Stick to EF APIs.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `SQLite Error 1: no such table` | `dotnet ef database update --project src/MogMatch.Web` |
| `The model for context has pending changes` | you changed an entity without adding a migration |
| Migration conflict after pulling `main` | remove *your unmerged* migration (`dotnet ef migrations remove`), pull, re-add it |
| Local DB in a weird state (dev only) | delete `mogmatch.db`, run `database update` again |
| `A second operation was started on this context` | you're sharing a context across concurrent calls — use `IDbContextFactory` and `await using` per operation |
