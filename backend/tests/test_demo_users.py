import pytest

from app.demo_users import DEMO_PASSWORD, DEMO_USERS
from app.seed import seed_test_users
from app.services.mog_score import TIERS
from app.services.profile_service import USERNAME_PATTERN
from app.services.tech_catalog import normalize_technology


@pytest.fixture
def seeded(app):
    seed_test_users()
    return app


def test_demo_usernames_are_valid_and_unique():
    names = [u["username"] for u in DEMO_USERS]
    assert len(names) == len(set(names))
    assert all(USERNAME_PATTERN.match(name) for name in names)


def test_demo_skills_and_technologies_are_in_the_catalog():
    # So the Edit Profile form accepts them if someone saves without changes.
    for user in DEMO_USERS:
        techs = user["skills"] + [t for p in user["projects"] for t in p["technologies"]]
        assert all(normalize_technology(t) for t in techs), user["username"]


def test_every_tier_has_demo_users():
    tiers = {u["tier"] for u in DEMO_USERS}
    assert tiers == {name for _, name, _, _ in TIERS}


def test_each_demo_user_logs_in_and_lands_in_its_tier(seeded):
    for user in DEMO_USERS:
        client = seeded.test_client()
        login = client.post("/api/auth/login", json={"username": user["username"], "password": DEMO_PASSWORD})
        assert login.status_code == 200, user["username"]
        mog = client.get("/api/profiles/me").get_json()["mog"]
        assert mog["tier"] == user["tier"], (user["username"], mog["score"])


def test_discover_can_sort_them_by_mog(seeded, client):
    profiles = client.get("/api/profiles?sort=mog").get_json()["profiles"]
    scores = [p["mog"]["score"] for p in profiles]
    assert scores == sorted(scores, reverse=True)
    names = [p["username"] for p in profiles]
    assert names.index("gigachad") < names.index("ghostdev")  # top mogger before the emptiest profile


def test_every_test_account_has_its_own_valid_theme(seeded):
    from app.demo_users import DEMO_THEMES
    from app.seed import test_accounts
    from app.services.profile_service import _clean_theme

    names = [account["username"] for account in test_accounts()]
    assert set(DEMO_THEMES) == set(names)  # nobody left on the default look
    backgrounds = [theme["background"] for theme in DEMO_THEMES.values()]
    assert len(backgrounds) == len(set(backgrounds))  # no two share a background
    for name, theme in DEMO_THEMES.items():
        errors: dict = {}
        _clean_theme(theme, errors)  # same rules as saving it in Edit Profile
        assert errors == {}, (name, errors)


def test_themes_come_back_from_the_api(seeded):
    from app.demo_users import DEMO_THEMES

    client = seeded.test_client()
    client.post("/api/auth/login", json={"username": "gigachad", "password": DEMO_PASSWORD})
    theme = client.get("/api/profiles/me").get_json()["theme"]
    assert theme["background"] == DEMO_THEMES["gigachad"]["background"]
    assert theme["effect"] == "matrix"
    assert theme["effect_options"]["rain_color"] == "#b388ff"
