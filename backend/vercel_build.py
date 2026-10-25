"""Runs during every Vercel deploy (the "api" service's buildCommand in vercel.json), before the new
version goes live: brings the production database up to date and fills in demo data.

1. Apply migrations (same as `flask db upgrade`), so new tables/columns exist.
2. `flask seed`: adds the seeded accounts and their SEED_PASSWORD if missing. It never overwrites
   edited data, so running it on every deploy is safe.
3. Only if SEED_DEMO_USERS=1: also add user1/user2 and the 50 demo users (`flask seed-test-users`).
   Their passwords are public in this repo, so anyone could log in as them. Fine for a demo.

Run it locally to check it works: `python vercel_build.py` (uses your backend/.env database).
"""

import os
import sys
from pathlib import Path

from flask_migrate import upgrade

from app import create_app
from app.seed import seed_database, seed_test_users

MIGRATIONS_DIR = str(Path(__file__).resolve().parent / "migrations")


def main(test_config: dict | None = None) -> int:
    # On Vercel, create_app refuses to run without DATABASE_URL or a real SECRET_KEY.
    # `test_config` lets tests point it at a throwaway database.
    app = create_app(test_config)
    with app.app_context():
        print("[vercel_build] applying migrations...")
        upgrade(directory=MIGRATIONS_DIR)
        counts = seed_database()
        print(f"[vercel_build] seed: {counts['created']} created, {counts['skipped']} already there")
        if os.getenv("SEED_DEMO_USERS") == "1":
            created = seed_test_users()
            print(f"[vercel_build] demo users: {created} created (password in backend/app/demo_users.py)")
        else:
            print("[vercel_build] demo users skipped (set SEED_DEMO_USERS=1 to add them)")
    print("[vercel_build] database ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
