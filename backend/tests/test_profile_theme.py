import pytest


DEFAULT_OPTIONS = {
    "brightness": 40, "size": 14, "speed": 4, "glow": False,
    "count": 1, "color_change": True, "color": "#ffffff",
    "rain_color": "#22ff66", "rain_rainbow": False, "rain_symbols": "katakana",
    "emojis": ["🚀", "✨", "🔥", "💻", "🦄", "🍕"], "emoji_count": 14, "emoji_angle": 45,
    "emoji_path": "straight", "emoji_spin": 2,
}
DEFAULT_THEME = {"background": None, "effect": None, "effect_options": DEFAULT_OPTIONS}


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
    assert response.get_json()["theme"] == {**DEFAULT_THEME, "background": "#04130a", "effect": "matrix"}

    me = client.get("/api/profiles/me").get_json()
    assert me["theme"] == {**DEFAULT_THEME, "background": "#04130a", "effect": "matrix"}
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_effect_works_without_a_custom_background(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix"}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {**DEFAULT_THEME, "effect": "matrix"}


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


CRANKED = {
    "brightness": 100, "size": 48, "speed": 10, "glow": True,
    "count": 10, "color_change": False, "color": "#ff00ff",
    "rain_color": "#00ffff", "rain_rainbow": True, "rain_symbols": "chaos",
    "emojis": ["👻", "🎃"], "emoji_count": 60, "emoji_angle": 359, "emoji_path": "bounce", "emoji_spin": -10,
}


def test_effect_options_persist_and_show_up_for_other_viewers(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"] == CRANKED

    me = client.get("/api/profiles/me").get_json()
    assert me["theme"]["effect_options"] == CRANKED
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"]["effect_options"] == CRANKED


def test_partial_effect_options_fall_back_to_defaults(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": {"size": 30}}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"] == {**DEFAULT_OPTIONS, "size": 30}


def test_effect_options_survive_turning_the_effect_off(client):
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})

    response = client.patch("/api/profiles/me", json={"theme": {"effect": None, "effect_options": CRANKED}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {**DEFAULT_THEME, "effect_options": CRANKED}


def test_resetting_the_theme_clears_effect_options(client):
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})

    response = client.patch("/api/profiles/me", json={"theme": {}})

    assert response.get_json()["theme"] == DEFAULT_THEME


def test_updating_other_fields_keeps_effect_options(client):
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})
    client.patch("/api/profiles/me", json={"full_name": "Jordan A."})

    assert _theme(client)["effect_options"] == CRANKED


@pytest.mark.parametrize(
    "option, value",
    [
        ("size", 9), ("size", 49), ("size", 14.5), ("size", "14"), ("size", True), ("size", None),
        ("brightness", 0), ("brightness", 101), ("brightness", -5),
        ("speed", 0), ("speed", 11), ("speed", [4]),
        ("glow", 1), ("glow", "yes"), ("glow", None),
        ("count", 0), ("count", 11), ("count", 2.5), ("count", True),
        ("color_change", 0), ("color_change", "no"), ("color_change", None),
        ("color", "red"), ("color", "#fff"), ("color", "#gggggg"), ("color", 255), ("color", "#ff00ff;x"), ("color", None),
        ("rain_color", "green"), ("rain_color", "#0f0"), ("rain_color", 0x00FF00), ("rain_color", "#00ff00;x"), ("rain_color", None),
        ("rain_rainbow", 1), ("rain_rainbow", "on"), ("rain_rainbow", None),
        ("rain_symbols", "emoji"), ("rain_symbols", "Binary"), ("rain_symbols", ""), ("rain_symbols", 1),
        ("rain_symbols", ["binary"]), ("rain_symbols", None),
    ],
)
def test_effect_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


@pytest.mark.parametrize("value", [10, 48, 14])
def test_effect_option_range_edges_are_accepted(client, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"size": value}}})

    assert response.status_code == 200, response.get_json()


def test_effect_options_reject_unknown_keys_and_wrong_shape(client):
    unknown = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"color": "red"}}})
    assert unknown.status_code == 400
    assert "theme.effect_options.color" in unknown.get_json()["error"]["fields"]

    wrong_shape = client.patch("/api/profiles/me", json={"theme": {"effect_options": [1, 2]}})
    assert wrong_shape.status_code == 400
    assert "theme.effect_options" in wrong_shape.get_json()["error"]["fields"]


def test_effect_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


def test_bouncing_dvd_effect_persists_with_its_own_tuning(client):
    options = {**DEFAULT_OPTIONS, "brightness": 100, "size": 20, "speed": 8, "count": 4, "glow": True, "color_change": False, "color": "#00ffcc"}
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#000000", "effect": "dvd", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#000000", "effect": "dvd", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_switching_effects_keeps_the_tuning(client):
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": CRANKED}})

    response = client.patch("/api/profiles/me", json={"theme": {"effect": "dvd", "effect_options": CRANKED}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {**DEFAULT_THEME, "effect": "dvd", "effect_options": CRANKED}


def test_dvd_color_is_trimmed_and_lowercased(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"color": " #FF00AA "}}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["color"] == "#ff00aa"


def test_a_logo_color_does_not_need_to_be_dark(client):
    # Unlike the card background, this is drawn on a canvas and never sits behind text as a fill.
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"color": "#ffffff"}}})

    assert response.status_code == 200, response.get_json()


def test_old_saved_options_get_the_new_defaults(client):
    # A profile saved before count/color existed only has the older keys; reading it must still give a full set.
    client.patch("/api/profiles/me", json={"theme": {"effect": "dvd", "effect_options": {"size": 20, "glow": True}}})

    options = _theme(client)["effect_options"]
    assert options == {**DEFAULT_OPTIONS, "size": 20, "glow": True}


@pytest.mark.parametrize("symbols", ["katakana", "binary", "code", "chaos"])
def test_every_rain_symbol_set_is_accepted_and_persists(client, symbols):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": {"rain_symbols": symbols}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["rain_symbols"] == symbols


def test_rain_color_is_trimmed_and_lowercased_and_may_be_any_brightness(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"rain_color": " #FF2BD6 "}}})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["rain_color"] == "#ff2bd6"

    # Drawn on a canvas, never behind text as a fill, so unlike the background there is no darkness rule.
    assert client.patch("/api/profiles/me", json={"theme": {"effect_options": {"rain_color": "#ffffff"}}}).status_code == 200


def test_rain_and_logo_colors_are_independent(client):
    client.patch("/api/profiles/me", json={"theme": {"effect_options": {"rain_color": "#ff0000"}}})

    options = _theme(client)["effect_options"]
    assert options["rain_color"] == "#ff0000"
    assert options["color"] == "#ffffff"  # the DVD logo's own default is untouched


def test_existing_matrix_themes_keep_their_green_default(client):
    # A profile saved before the rain had colors or symbols must still look the same.
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": {"size": 20}}})

    options = _theme(client)["effect_options"]
    assert (options["rain_color"], options["rain_rainbow"], options["rain_symbols"]) == ("#22ff66", False, "katakana")


# ---------- floating emoji ----------

def test_emoji_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 90, "size": 30, "speed": 6, "glow": True,
        "emojis": ["🎉", "🥳"], "emoji_count": 24, "emoji_angle": 90, "emoji_path": "wave", "emoji_spin": -3,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#1e0a2e", "effect": "emoji", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#1e0a2e", "effect": "emoji", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_emoji_defaults_are_fun_and_not_shared_between_responses(client):
    options = _theme(client)["effect_options"]
    assert options["emojis"] == ["🚀", "✨", "🔥", "💻", "🦄", "🍕"]
    assert (options["emoji_count"], options["emoji_angle"], options["emoji_path"], options["emoji_spin"]) == (14, 45, "straight", 2)


@pytest.mark.parametrize("path", ["straight", "wave", "bounce"])
def test_every_emoji_path_is_accepted_and_persists(client, path):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "emoji", "effect_options": {"emoji_path": path}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["emoji_path"] == path


@pytest.mark.parametrize(
    "emoji",
    ["🚀", "❤️", "👍🏽", "🇺🇸", "👩\u200d💻", "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f", "☄️", "🕸️"],
)
def test_emoji_of_every_shape_are_accepted(client, emoji):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"emojis": [emoji]}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["emojis"] == [emoji]


def test_emoji_are_trimmed_and_deduplicated_in_order(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"emojis": [" 🔥 ", "🚀", "🔥", "🚀"]}}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["emojis"] == ["🔥", "🚀"]


@pytest.mark.parametrize(
    "emojis",
    [
        [], "🚀", None, 5, {"a": "🚀"},                      # not a list, or empty
        ["a"], ["hello"], ["1"], ["#"], [" "], [""],          # words, digits, ASCII, blanks
        ["<script>"], ["🚀<b>"], ["🚀 x"], ["🚀\n🔥"], ["é"],  # markup or letters mixed in
        ["\u200d"], ["\ufe0f"],                              # invisible characters only
        [1], [None], [["🚀"]], [{"e": "🚀"}], ["🚀", 7],      # wrong item types
        ["🚀", "x"],                                          # one bad item spoils the list
        ["🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"],                        # too long to be one emoji
        ["🌀", "🌁", "🌂", "🌃", "🌄", "🌅", "🌆", "🌇", "🌈", "🌉", "🌊", "🌋", "🌌"],  # 13 distinct: too many
    ],
)
def test_bad_emoji_lists_are_rejected(client, emojis):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "emoji", "effect_options": {"emojis": emojis}}})

    assert response.status_code == 400
    assert "theme.effect_options.emojis" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_twelve_emoji_is_the_limit(client):
    twelve = ["🌀", "🌁", "🌂", "🌃", "🌄", "🌅", "🌆", "🌇", "🌈", "🌉", "🌊", "🌋"]

    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"emojis": twelve}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["emojis"] == twelve


@pytest.mark.parametrize(
    "option, value",
    [
        ("emoji_count", 2), ("emoji_count", 61), ("emoji_count", 5.5), ("emoji_count", True), ("emoji_count", "10"),
        ("emoji_angle", -1), ("emoji_angle", 360), ("emoji_angle", 45.5), ("emoji_angle", None), ("emoji_angle", False),
        ("emoji_spin", -11), ("emoji_spin", 11), ("emoji_spin", 0.5), ("emoji_spin", "1"), ("emoji_spin", True),
        ("emoji_path", "zigzag"), ("emoji_path", "Wave"), ("emoji_path", ""), ("emoji_path", 1), ("emoji_path", ["wave"]),
        ("emoji_path", None),
    ],
)
def test_emoji_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "emoji", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


@pytest.mark.parametrize(
    "option, value",
    [("emoji_count", 3), ("emoji_count", 60), ("emoji_angle", 0), ("emoji_angle", 359), ("emoji_spin", -10), ("emoji_spin", 0), ("emoji_spin", 10)],
)
def test_emoji_option_range_edges_are_accepted(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


def test_old_saved_options_get_the_emoji_defaults(client):
    # A profile saved before the emoji effect existed must still read back a full set of options.
    client.patch("/api/profiles/me", json={"theme": {"effect": "matrix", "effect_options": {"size": 20}}})

    options = _theme(client)["effect_options"]
    assert options["emojis"] == DEFAULT_OPTIONS["emojis"]
    assert options["emoji_path"] == "straight"


def test_emoji_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "emoji", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before
