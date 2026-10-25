import pytest

pytestmark = pytest.mark.usefixtures("blank_looks")  # these start from the default look

DEFAULT_OPTIONS = {
    "brightness": 40, "size": 14, "speed": 4, "glow": False,
    "count": 1, "color_change": True, "color": "#ffffff",
    "rain_color": "#22ff66", "rain_rainbow": False, "rain_symbols": "katakana",
    "emojis": ["🚀", "✨", "🔥", "💻", "🦄", "🍕"], "emoji_count": 14, "emoji_angle": 45,
    "emoji_path": "straight", "emoji_spin": 2,
    "slogans": ["NEVER SKIP LEG DAY", "ONE MORE REP", "LIGHT WEIGHT BABY", "DO YOU EVEN LIFT?", "MOGGED"],
    "slogan_color": "#ff4d2e", "slogan_style": "mixed", "slogan_tilt": -8, "slogan_alternate": True,
    "chart_volatility": 6, "chart_mood": "choppy", "chart_palette": "classic", "chart_ticker": "MOG", "chart_label": True,
    "money_kind": "bills", "money_count": 30, "money_wind": 5, "money_weight": 5,
    "snow_kind": "mixed", "snow_count": 80, "snow_wind": 2,
    "lightning_color": "#9ec5ff", "lightning_strikes": 6, "lightning_forks": 5, "lightning_flash": True,
    "tron_color": "#22d3ee", "tron_cycles": 3, "tron_tail": 5, "tron_grid": True,
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
    "slogans": ["LET'S GOOO", "STAY HARD"], "slogan_color": "#00ffcc", "slogan_style": "outline",
    "slogan_tilt": 45, "slogan_alternate": False,
    "chart_volatility": 10, "chart_mood": "bull", "chart_palette": "neon", "chart_ticker": "GIGA42", "chart_label": False,
    "money_kind": "mixed", "money_count": 80, "money_wind": 10, "money_weight": 10,
    "snow_kind": "crystals", "snow_count": 200, "snow_wind": -10,
    "lightning_color": "#ffd84a", "lightning_strikes": 10, "lightning_forks": 10, "lightning_flash": False,
    "tron_color": "#ff8a00", "tron_cycles": 10, "tron_tail": 10, "tron_grid": False,
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


# ---------- scrolling slogans ----------

def test_slogans_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 45, "size": 22, "speed": 6, "glow": True,
        "slogans": ["GIT PUSH --FORCE", "SQUATS > STANDUPS"], "slogan_color": "#ffd60a",
        "slogan_style": "solid", "slogan_tilt": 12, "slogan_alternate": False,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#050816", "effect": "slogans", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#050816", "effect": "slogans", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_slogan_defaults_are_gym_bro_speak(client):
    options = _theme(client)["effect_options"]
    assert options["slogans"][:2] == ["NEVER SKIP LEG DAY", "ONE MORE REP"]
    assert (options["slogan_style"], options["slogan_tilt"], options["slogan_alternate"]) == ("mixed", -8, True)


@pytest.mark.parametrize(
    "slogan",
    ["ONE MORE REP", "git push --force", "💪 PUMP 💪", "ÑANDÚ MOGS", "DO YOU EVEN LIFT?", "x", "A" * 40, "<b>bold</b> & \"quotes\""],
)
def test_slogans_of_every_shape_are_accepted(client, slogan):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"slogans": [slogan]}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["slogans"] == [slogan]


def test_slogans_are_tidied_and_deduplicated_ignoring_case(client):
    slogans = ["  ONE   MORE\tREP ", "one more rep", "Light Weight", "LIGHT WEIGHT"]
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"slogans": slogans}}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["slogans"] == ["ONE MORE REP", "Light Weight"]


@pytest.mark.parametrize(
    "slogans",
    [
        [], "ONE MORE REP", None, 5, {"a": "REP"},                    # not a list, or empty
        [""], ["   "], ["\n\t"],                                    # blank
        ["A" * 41],                                                  # too long
        ["REP\x00"], ["REP\x07"], ["REP\ue000"],                    # control and private-use characters
        ["REP\u202eSDRAWKCAB"], ["\u2066REP"],                      # text-direction tricks
        [1], [None], [["REP"]], [{"s": "REP"}], ["REP", 7],          # wrong item types
        ["FINE", ""],                                                # one bad slogan spoils the list
        [f"SLOGAN {n}" for n in range(9)],                           # 9 distinct: too many
    ],
)
def test_bad_slogan_lists_are_rejected(client, slogans):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "slogans", "effect_options": {"slogans": slogans}}})

    assert response.status_code == 400
    assert "theme.effect_options.slogans" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_eight_slogans_is_the_limit(client):
    eight = [f"SLOGAN {n}" for n in range(8)]

    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"slogans": eight}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["slogans"] == eight


@pytest.mark.parametrize("style", ["solid", "outline", "mixed"])
def test_every_slogan_style_is_accepted(client, style):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "slogans", "effect_options": {"slogan_style": style}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["slogan_style"] == style


def test_slogan_color_is_trimmed_and_lowercased_and_may_be_any_brightness(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"slogan_color": " #FFD60A "}}})
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["slogan_color"] == "#ffd60a"

    assert client.patch("/api/profiles/me", json={"theme": {"effect_options": {"slogan_color": "#ffffff"}}}).status_code == 200


@pytest.mark.parametrize(
    "option, value",
    [
        ("slogan_tilt", -46), ("slogan_tilt", 46), ("slogan_tilt", 2.5), ("slogan_tilt", "10"), ("slogan_tilt", True), ("slogan_tilt", None),
        ("slogan_style", "dotted"), ("slogan_style", "Solid"), ("slogan_style", ""), ("slogan_style", 1), ("slogan_style", None),
        ("slogan_color", "red"), ("slogan_color", "#fff"), ("slogan_color", 0xFFD60A), ("slogan_color", "#ffd60a;x"), ("slogan_color", None),
        ("slogan_alternate", 1), ("slogan_alternate", "yes"), ("slogan_alternate", None),
    ],
)
def test_slogan_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "slogans", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


@pytest.mark.parametrize("option, value", [("slogan_tilt", -45), ("slogan_tilt", 0), ("slogan_tilt", 45)])
def test_slogan_tilt_edges_are_accepted(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


def test_slogan_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "slogans", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


# ---------- volatile market ----------

def test_market_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 55, "size": 18, "speed": 7, "glow": True,
        "chart_volatility": 9, "chart_mood": "bear", "chart_palette": "swapped", "chart_ticker": "REKT", "chart_label": False,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#050a14", "effect": "market", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#050a14", "effect": "market", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_market_defaults_are_a_choppy_classic_chart_called_mog(client):
    options = _theme(client)["effect_options"]
    assert (options["chart_volatility"], options["chart_mood"], options["chart_palette"]) == (6, "choppy", "classic")
    assert (options["chart_ticker"], options["chart_label"]) == ("MOG", True)


@pytest.mark.parametrize("option, value", [("chart_mood", "bull"), ("chart_mood", "bear"), ("chart_mood", "choppy"),
                                           ("chart_palette", "classic"), ("chart_palette", "swapped"), ("chart_palette", "neon"), ("chart_palette", "mono"),
                                           ("chart_volatility", 1), ("chart_volatility", 10), ("chart_label", True), ("chart_label", False)])
def test_market_option_values_are_accepted_and_persist(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "market", "effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


@pytest.mark.parametrize("ticker, expected", [("MOG", "MOG"), ("giga", "GIGA"), ("  mog42 ", "MOG42"), ("A", "A"), ("ABCDEFGH", "ABCDEFGH"), ("007", "007")])
def test_ticker_is_trimmed_and_uppercased(client, ticker, expected):
    response = client.patch("/api/profiles/me", json={"theme": {"effect_options": {"chart_ticker": ticker}}})

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"]["effect_options"]["chart_ticker"] == expected


@pytest.mark.parametrize(
    "option, value",
    [
        ("chart_ticker", ""), ("chart_ticker", "   "), ("chart_ticker", "ABCDEFGHI"), ("chart_ticker", "AB CD"), ("chart_ticker", "$MOG"),
        ("chart_ticker", "A-B"), ("chart_ticker", "<b>"), ("chart_ticker", "ÅNGEL"), ("chart_ticker", "MO\nG"), ("chart_ticker", 5),
        ("chart_ticker", None), ("chart_ticker", ["MOG"]),
        ("chart_volatility", 0), ("chart_volatility", 11), ("chart_volatility", 5.5), ("chart_volatility", "5"), ("chart_volatility", True), ("chart_volatility", None),
        ("chart_mood", "sideways"), ("chart_mood", "Bull"), ("chart_mood", ""), ("chart_mood", 1), ("chart_mood", ["bull"]), ("chart_mood", None),
        ("chart_palette", "rainbow"), ("chart_palette", "Neon"), ("chart_palette", ""), ("chart_palette", 2), ("chart_palette", None),
        ("chart_label", 1), ("chart_label", "yes"), ("chart_label", None),
    ],
)
def test_market_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "market", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_market_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "market", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


# ---------- money rain ----------

def test_money_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 65, "size": 18, "speed": 6, "glow": True,
        "money_kind": "coins", "money_count": 45, "money_wind": 9, "money_weight": 8,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#04150b", "effect": "money", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#04150b", "effect": "money", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_money_defaults_are_a_moderate_shower_of_bills_in_a_breeze(client):
    options = _theme(client)["effect_options"]
    assert (options["money_kind"], options["money_count"], options["money_wind"], options["money_weight"]) == ("bills", 30, 5, 5)


@pytest.mark.parametrize("option, value", [("money_kind", "bills"), ("money_kind", "coins"), ("money_kind", "mixed"),
                                           ("money_count", 5), ("money_count", 80), ("money_wind", 0), ("money_wind", 10),
                                           ("money_weight", 1), ("money_weight", 10)])
def test_money_option_values_are_accepted_and_persist(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "money", "effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


@pytest.mark.parametrize(
    "option, value",
    [
        ("money_kind", "cash"), ("money_kind", "Bills"), ("money_kind", ""), ("money_kind", 1), ("money_kind", ["bills"]), ("money_kind", None),
        ("money_count", 4), ("money_count", 81), ("money_count", 12.5), ("money_count", "30"), ("money_count", True), ("money_count", None),
        ("money_wind", -1), ("money_wind", 11), ("money_wind", 2.5), ("money_wind", "5"), ("money_wind", False), ("money_wind", None),
        ("money_weight", 0), ("money_weight", 11), ("money_weight", 5.5), ("money_weight", "5"), ("money_weight", True), ("money_weight", None),
    ],
)
def test_money_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "money", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_money_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "money", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


# ---------- snowfall ----------

def test_snow_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 70, "size": 20, "speed": 6, "glow": True,
        "snow_kind": "crystals", "snow_count": 150, "snow_wind": -7,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#0a1428", "effect": "snow", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#0a1428", "effect": "snow", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_snow_defaults_are_a_gentle_mixed_flurry_drifting_a_little_to_the_right(client):
    options = _theme(client)["effect_options"]
    assert (options["snow_kind"], options["snow_count"], options["snow_wind"]) == ("mixed", 80, 2)


@pytest.mark.parametrize("option, value", [("snow_kind", "dots"), ("snow_kind", "crystals"), ("snow_kind", "mixed"),
                                           ("snow_count", 20), ("snow_count", 200), ("snow_wind", -10), ("snow_wind", 0), ("snow_wind", 10)])
def test_snow_option_values_are_accepted_and_persist(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "snow", "effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


@pytest.mark.parametrize(
    "option, value",
    [
        ("snow_kind", "hail"), ("snow_kind", "Dots"), ("snow_kind", ""), ("snow_kind", 1), ("snow_kind", ["dots"]), ("snow_kind", None),
        ("snow_count", 19), ("snow_count", 201), ("snow_count", 80.5), ("snow_count", "80"), ("snow_count", True), ("snow_count", None),
        ("snow_wind", -11), ("snow_wind", 11), ("snow_wind", 2.5), ("snow_wind", "2"), ("snow_wind", False), ("snow_wind", None),
    ],
)
def test_snow_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "snow", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_snow_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "snow", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


# ---------- lightning ----------

def test_lightning_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 80, "size": 20, "glow": True,
        "lightning_color": "#b794ff", "lightning_strikes": 3, "lightning_forks": 8, "lightning_flash": False,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#070b18", "effect": "lightning", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#070b18", "effect": "lightning", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_lightning_defaults_are_forked_electric_blue_bolts_that_light_up_the_sky(client):
    options = _theme(client)["effect_options"]
    assert (options["lightning_color"], options["lightning_strikes"], options["lightning_forks"], options["lightning_flash"]) == (
        "#9ec5ff", 6, 5, True,
    )


@pytest.mark.parametrize("option, value", [("lightning_strikes", 1), ("lightning_strikes", 10), ("lightning_forks", 0), ("lightning_forks", 10),
                                           ("lightning_flash", True), ("lightning_flash", False)])
def test_lightning_option_values_are_accepted_and_persist(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "lightning", "effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


def test_lightning_color_is_trimmed_and_lowercased_and_may_be_any_brightness(client):
    response = client.patch(
        "/api/profiles/me", json={"theme": {"effect": "lightning", "effect_options": {"lightning_color": " #FFFFFF "}}}
    )

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["lightning_color"] == "#ffffff"


@pytest.mark.parametrize(
    "option, value",
    [
        ("lightning_strikes", 0), ("lightning_strikes", 11), ("lightning_strikes", 5.5), ("lightning_strikes", "5"), ("lightning_strikes", True), ("lightning_strikes", None),
        ("lightning_forks", -1), ("lightning_forks", 11), ("lightning_forks", 2.5), ("lightning_forks", "2"), ("lightning_forks", False), ("lightning_forks", None),
        ("lightning_flash", 1), ("lightning_flash", "true"), ("lightning_flash", None),
        ("lightning_color", "blue"), ("lightning_color", "#fff"), ("lightning_color", "#12345g"), ("lightning_color", "url(x)"), ("lightning_color", 5), ("lightning_color", None),
    ],
)
def test_lightning_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "lightning", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_lightning_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "lightning", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


# ---------- light cycles ----------

def test_tron_effect_persists_with_its_own_tuning(client):
    options = {
        **DEFAULT_OPTIONS, "brightness": 70, "size": 18, "speed": 7, "glow": True,
        "tron_color": "#ff8a00", "tron_cycles": 6, "tron_tail": 8, "tron_grid": False,
    }
    response = client.patch(
        "/api/profiles/me", json={"theme": {"background": "#020a14", "effect": "tron", "effect_options": options}}
    )
    assert response.status_code == 200, response.get_json()
    assert response.get_json()["theme"] == {"background": "#020a14", "effect": "tron", "effect_options": options}

    me = client.get("/api/profiles/me").get_json()
    assert client.get(f"/api/profiles/{me['id']}").get_json()["theme"] == me["theme"]


def test_tron_defaults_are_a_few_cyan_cycles_on_a_visible_grid(client):
    options = _theme(client)["effect_options"]
    assert (options["tron_color"], options["tron_cycles"], options["tron_tail"], options["tron_grid"]) == ("#22d3ee", 3, 5, True)


@pytest.mark.parametrize("option, value", [("tron_cycles", 1), ("tron_cycles", 10), ("tron_tail", 1), ("tron_tail", 10),
                                           ("tron_grid", True), ("tron_grid", False)])
def test_tron_option_values_are_accepted_and_persist(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "tron", "effect_options": {option: value}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"][option] == value


def test_tron_color_is_trimmed_and_lowercased_and_may_be_any_brightness(client):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "tron", "effect_options": {"tron_color": " #FFFFFF "}}})

    assert response.status_code == 200, response.get_json()
    assert _theme(client)["effect_options"]["tron_color"] == "#ffffff"


@pytest.mark.parametrize(
    "option, value",
    [
        ("tron_cycles", 0), ("tron_cycles", 11), ("tron_cycles", 2.5), ("tron_cycles", "3"), ("tron_cycles", True), ("tron_cycles", None),
        ("tron_tail", 0), ("tron_tail", 11), ("tron_tail", 5.5), ("tron_tail", "5"), ("tron_tail", False), ("tron_tail", None),
        ("tron_grid", 1), ("tron_grid", "true"), ("tron_grid", None),
        ("tron_color", "cyan"), ("tron_color", "#fff"), ("tron_color", "#22d3eg"), ("tron_color", "url(x)"), ("tron_color", 5), ("tron_color", None),
    ],
)
def test_tron_options_out_of_range_or_wrong_type_are_rejected(client, option, value):
    response = client.patch("/api/profiles/me", json={"theme": {"effect": "tron", "effect_options": {option: value}}})

    assert response.status_code == 400
    assert f"theme.effect_options.{option}" in response.get_json()["error"]["fields"]
    assert _theme(client) == DEFAULT_THEME  # nothing was saved


def test_tron_options_do_not_change_the_mog_score(client):
    before = client.get("/api/profiles/me").get_json()["mog"]
    client.patch("/api/profiles/me", json={"theme": {"effect": "tron", "effect_options": CRANKED}})

    assert client.get("/api/profiles/me").get_json()["mog"] == before


def test_old_saved_options_get_the_tron_defaults(client):
    # A profile saved before the light cycles existed must still read back a full set of options.
    client.patch("/api/profiles/me", json={"theme": {"effect": "lightning", "effect_options": {"size": 20}}})

    options = _theme(client)["effect_options"]
    assert (options["tron_color"], options["tron_cycles"], options["tron_tail"], options["tron_grid"]) == ("#22d3ee", 3, 5, True)


# ---------- themes saved by an older version ----------

def test_a_retired_effect_and_its_options_read_back_as_the_default_look(client, app):
    # An effect that was later removed (the barbell) and its options are still sitting in the database.
    from app.extensions import db
    from app.models import Profile

    with app.app_context():
        profile = Profile.query.filter_by(username=client.get("/api/profiles/me").get_json()["username"]).one()
        profile.theme = {
            "background": "#172554",
            "effect": "barbell",
            "effect_options": {"brightness": 70, "gym_plates": 4, "gym_label": True},
        }
        db.session.commit()

    theme = _theme(client)
    assert theme["effect"] is None
    assert theme["background"] == "#172554"  # what is still valid is kept
    assert theme["effect_options"] == {**DEFAULT_OPTIONS, "brightness": 70}  # and the retired options are gone

    # So the edit form can send it straight back without a 400.
    assert client.patch("/api/profiles/me", json={"theme": theme}).status_code == 200
