import vercel_build
from app.models import Invite, Profile


def test_build_script_migrates_and_seeds_an_empty_database(tmp_path, monkeypatch):
    # A brand-new database, like the first deploy to a fresh Neon/Postgres.
    url = f"sqlite:///{(tmp_path / 'deploy.db').as_posix()}"
    monkeypatch.delenv("SEED_DEMO_USERS", raising=False)
    assert vercel_build.main({"SQLALCHEMY_DATABASE_URI": url}) == 0

    app = vercel_build.create_app({"SQLALCHEMY_DATABASE_URI": url})
    with app.app_context():
        assert Profile.query.filter_by(username="jordan-dev").one()  # seeded, with a password
        assert Profile.query.filter_by(username="gigachad").first() is None  # demo users are opt-in
        seeded_invites = Invite.query.count()

    # Running it again (every redeploy) changes nothing; with SEED_DEMO_USERS=1 it adds the demo users.
    monkeypatch.setenv("SEED_DEMO_USERS", "1")
    assert vercel_build.main({"SQLALCHEMY_DATABASE_URI": url}) == 0
    with app.app_context():
        assert Invite.query.count() == seeded_invites
        assert Profile.query.filter_by(username="gigachad").one()
        login = app.test_client().post("/api/auth/login", json={"username": "gigachad", "password": "123"})
        assert login.status_code == 200
