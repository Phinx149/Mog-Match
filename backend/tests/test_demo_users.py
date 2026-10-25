from io import BytesIO
from urllib.parse import urlsplit

import pytest
from PIL import Image

from app.demo_users import DEMO_PASSWORD, DEMO_THEMES, DEMO_USERS, SEED_THEMES
from app.extensions import db
from app.models import Profile
from app.seed import AVATAR_DIR, DEMO_PROFILE, SEED_PROFILES, TEST_USERS, seed_database, seed_test_users
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
    for user in DEMO_USERS + TEST_USERS:
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


# ---------- profile pictures and themes: nobody is left with initials and the default look

def test_every_account_without_an_avatar_link_has_exactly_one_picture():
    from app.seed import test_accounts

    seeded = [DEMO_PROFILE] + SEED_PROFILES + test_accounts()
    needs_picture = {data["username"] for data in seeded if not data.get("avatar_url")}
    assert {path.stem for path in AVATAR_DIR.glob("*.png")} == needs_picture  # none missing, none left over


def test_seeded_pictures_are_small_square_pngs():
    for path in AVATAR_DIR.glob("*.png"):
        with Image.open(path) as image:
            assert image.format == "PNG" and image.width == image.height, path.name
        assert path.stat().st_size < 100_000, path.name  # they live in the database, keep them light


def test_every_seeded_account_has_a_picture_and_a_theme(seeded):
    from app.seed import test_accounts

    profiles = Profile.query.all()
    assert len(profiles) == 1 + len(SEED_PROFILES) + len(test_accounts())
    for profile in profiles:
        assert profile.user.photo_data or profile.avatar_url, profile.username
        assert profile.theme, profile.username


def test_seeded_picture_is_served_as_the_profile_photo(client):
    profile = client.get("/api/profiles/me").get_json()  # jordan-dev, made by `flask seed`
    image = client.get(urlsplit(profile["avatar_url"]).path)
    assert image.status_code == 200 and image.mimetype == "image/png"
    assert image.data == (AVATAR_DIR / "jordan-dev.png").read_bytes()
    assert Image.open(BytesIO(image.data)).size == (256, 256)


def test_seed_profiles_have_their_own_valid_themes():
    from app.services.profile_service import _clean_theme

    assert set(SEED_THEMES) == {DEMO_PROFILE["username"]} | {data["username"] for data in SEED_PROFILES}
    backgrounds = [theme["background"] for theme in [*SEED_THEMES.values(), *DEMO_THEMES.values()]]
    assert len(backgrounds) == len(set(backgrounds))  # nobody looks like a test account either
    for name, theme in SEED_THEMES.items():
        errors: dict = {}
        _clean_theme(theme, errors)
        assert errors == {}, (name, errors)


def test_reseeding_fills_a_missing_picture_and_theme_but_never_replaces_one(seeded):
    # Like accounts created before pictures and themes existed...
    jordan = Profile.query.filter_by(username="jordan-dev").one()
    jordan.user.photo_data, jordan.theme = None, None
    user1 = Profile.query.filter_by(username="user1").one()
    user1.user.photo_data = None
    # ...next to people who picked their own.
    maya = Profile.query.filter_by(username="mayacodes").one()
    maya.user.photo_data, maya.user.photo_mimetype, maya.theme = b"mine", "image/png", {"background": "#000000"}
    user2 = Profile.query.filter_by(username="user2").one()
    user2.user.photo_data, user2.avatar_url = None, "https://example.com/me.png"
    db.session.commit()

    seed_database()
    seed_test_users()

    assert jordan.user.photo_data == (AVATAR_DIR / "jordan-dev.png").read_bytes()
    assert jordan.theme == SEED_THEMES["jordan-dev"]
    assert user1.user.photo_data == (AVATAR_DIR / "user1.png").read_bytes()
    assert maya.user.photo_data == b"mine" and maya.theme == {"background": "#000000"}
    assert user2.user.photo_data is None and user2.avatar_url == "https://example.com/me.png"
