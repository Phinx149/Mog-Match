import pytest


DEFAULT_THEME = {"background": None, "effect": None}


def _theme(client):
    return client.get("/api/profiles/me").get_json()["theme"]


def test_profiles_default_to_no_custom_background(client):
    assert _theme(client) == DEFAULT_THEME
    for profile in client.get("/api/profiles").get_json()["profiles"]:
        assert profile["theme"] == DEFAULT_THEME


def test_background_persists_and_shows_up_for_other_viewers(client):
    # Normalized to lowercase and trimmed.
    response = client.patch("/api/profiles/me", json={"theme": {"background": " #172554 "}})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {**DEFAULT_THEME, "background": "#172554"}

    me = client.get("/api/profiles/me").get_json()
    assert me["theme"] == {**DEFAULT_THEME, "background": "#172554"}
    # Visitors load it from the by-id endpoint, so check that path too.
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == {**DEFAULT_THEME, "background": "#172554"}


def test_background_can_be_reset(client):
    client.patch("/api/profiles/me", json={"theme": {"background": "#172554"}})

    for reset in ({"background": None}, {}, None):
        client.patch("/api/profiles/me", json={"theme": {"background": "#172554"}})
        response = client.patch("/api/profiles/me", json={"theme": reset})
        assert response.status_code == 200, response.get_json()
        assert response.get_json()["theme"] == DEFAULT_THEME


def test_updating_other_fields_keeps_the_theme(client):
    client.patch("/api/profiles/me", json={"theme": {"background": "#172554"}})
    client.patch("/api/profiles/me", json={"full_name": "Jordan A."})

    assert _theme(client) == {**DEFAULT_THEME, "background": "#172554"}


@pytest.mark.parametrize(
    "value",
    ["red", "#fff", "#12345", "#172554;color:red", "url(javascript:alert(1))", "#gggggg", 123, ["#172554"]],
)
def test_background_must_be_a_hex_color(client, value):
    response = client.patch("/api/profiles/me", json={"theme": {"background": value}})

    assert response.status_code == 400
    assert "theme.background" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


@pytest.mark.parametrize("value", ["#ffffff", "#facc15", "#94a3b8", "#3b82f6"])
def test_background_too_light_for_the_text_is_rejected(client, value):
    response = client.patch("/api/profiles/me", json={"theme": {"background": value}})

    assert response.status_code == 400
    assert "too light" in response.get_json()["error"]["fields"]["theme.background"]


@pytest.mark.parametrize("value", ["#000000", "#0b0d14", "#312e81", "#172554", "#4c1d95", "#052e16"])
def test_dark_backgrounds_are_accepted(client, value):
    response = client.patch("/api/profiles/me", json={"theme": {"background": value}})

    assert response.status_code == 200, response.get_json()


def test_theme_rejects_unknown_options_and_wrong_shape(client):
    unknown = client.patch("/api/profiles/me", json={"theme": {"background": "#172554", "font": "Comic Sans"}})
    assert unknown.status_code == 400
    assert "theme.font" in unknown.get_json()["error"]["fields"]

    wrong_shape = client.patch("/api/profiles/me", json={"theme": "#172554"})
    assert wrong_shape.status_code == 400
    assert "theme" in wrong_shape.get_json()["error"]["fields"]


def test_theme_does_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"background": "#172554"}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


def test_effect_persists_alongside_the_background(client):
    response = client.patch("/api/profiles/me", json={"theme": {"background": "#04130a", "effect": "matrix"}})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#04130a", "effect": "matrix"}

    me = client.get("/api/profiles/me").get_json()
    assert me["theme"] == {"background": "#04130a", "effect": "matrix"}
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_effect_works_without_a_custom_background(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix"}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": None, "effect": "matrix"}


def test_effect_can_be_reset(client):
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix"}})

    response = client.patch("/api/profiles/me", json={"theme": {"effect": None}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == DEFAULT_THEME


@pytest.mark.parametrize("value", ["rain", "MATRIX", "", "<script>", 1, True, ["matrix"], {"name": "matrix"}])
def test_effect_must_be_a_known_name(client, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": value}})

    assert response.status_code == 400
    assert "theme.effect" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved
