---
name: db-migration
description: Add or change SQLAlchemy models, Flask-Migrate/Alembic migrations, or seed data in MogMatch's Flask backend. Use when someone says "add a column", "new table", "migration", "no such table", "flask db", "seed", "reset the database", or edits backend/app/models/ or backend/app/seed.py.
---

# Database Migration (Flask-SQLAlchemy + Flask-Migrate)

Run everything from `backend/` with the venv active. Schema overview: `docs/ARCHITECTURE.md#data-model`.

## Workflow
1. Edit/add the model in `app/models/` and export it from `app/models/__init__.py`.
2. Generate: `flask db migrate -m "add swipes table"`
3. **Open the new file in `migrations/versions/` and read it.** Autogenerate misses some things (renames look like drop+add; data changes aren't generated). Fix it by hand if needed.
4. Apply: `flask db upgrade`
5. Update `seed.py` if the feature needs demo data, `profile_service.to_dict` / `frontend/src/types/` if the API shape changes.
6. Run `pytest` (tests build the schema with `db.create_all()` from the models).
7. Commit the model change **and** the migration file together.

Never edit a migration that's already merged into `dev` — add a new one.

## Model conventions
```python
import uuid
from ..extensions import db
from .base import TimestampMixin

class Swipe(TimestampMixin, db.Model):
    __tablename__ = "swipes"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)          # UUID PKs everywhere
    swiper_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = db.Column(db.Uuid, db.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    action = db.Column(db.String(10), nullable=False)                      # validate values in the service

    __table_args__ = (db.UniqueConstraint("swiper_id", "target_id"),)
```
- List data → `db.Column(db.JSON, nullable=False, default=list)`. When updating, **assign a new list** (`profile.skills = [...]`); in-place `.append()` isn't detected.
- Owned children → `relationship(..., cascade="all, delete-orphan")` + `ondelete="CASCADE"` on the FK.
- Avoid SQLite-only SQL so `DATABASE_URL=postgresql://...` keeps working.
- Migrations run in batch mode (`render_as_batch=True`) so SQLite can alter tables.

## Seed data (`app/seed.py`)
- `flask seed` must stay **idempotent**: create what's missing, skip what exists, never overwrite edits.
- Destructive refresh only behind `flask seed --reset`.
- Look up seeded rows by stable keys (email / username), not by generated UUIDs.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `no such table` | `flask db upgrade` |
| `Target database is not up to date` | `flask db upgrade`, then migrate again |
| `Can't locate revision` / two heads after merging `dev` | `flask db heads`; if two, `flask db merge heads -m "merge"` then `flask db upgrade` |
| Autogenerate produced an empty migration | model not imported in `app/models/__init__.py` |
| Dev DB hopelessly out of sync (dev only!) | stop Flask, delete `instance/mogmatch.db`, `flask db upgrade && flask seed` |
