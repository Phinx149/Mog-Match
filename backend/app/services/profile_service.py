"""Profile reads, filtering, serialization and validated updates."""

import re
import hashlib
import unicodedata
import uuid
from typing import Any
from urllib.parse import urlparse

from flask import current_app, url_for
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Profile, ProfileLink, Project, User
from .mog_score import compute_mog_score, tier_floor
from .tech_catalog import ALL_TECHNOLOGIES, normalize_technology

EXPERIENCE_LEVELS = ("Student", "Junior", "Mid-level", "Senior", "Lead")
# What a profile can say it wants from a match. Fixed (not free text) so filtering and the
# Mog Score's shared-intent / Mentor-Mentee rules can rely on exact values. Order = display order.
LOOKING_FOR_OPTIONS = ("Hackathon team", "Side project", "Open source", "Cofounder", "Mentor", "Mentee", "Just vibes")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,40}$")

# field -> (max length, required)
STRING_FIELDS: dict[str, tuple[int, bool]] = {
    "full_name": (120, True),
    "username": (40, True),
    "avatar_url": (500, False),
    "location": (120, False),
    "education": (200, False),
    "bio": (2000, False),
    "favorite_ide": (80, False),
    "experience_level": (40, False),
}
# field -> max number of items
LIST_FIELDS: dict[str, int] = {
    "skills": 30,
    "interests": 30,
    "favorite_ai_agents": 10,
    "looking_for": 10,
}
MAX_TAG_LENGTH = 40
MAX_LINKS = 10
MAX_PROJECTS = 20

# Theme options a profile may set (purely cosmetic; never used for search, filtering or scoring).
THEME_FIELDS = ("background", "effect", "effect_options")
# Animated backgrounds the frontend knows how to draw (see ThemeScope.tsx). Keep in sync with
# THEME_EFFECTS in frontend/src/types/profile.ts. Only names are stored; the animation itself is code.
THEME_EFFECTS = ("matrix", "dvd", "emoji")
# Tuning shared by every effect (each reads them its own way, e.g. size = letter size or logo size,
# and an effect ignores options that don't apply to it, like the rain and `count`).
# Integers must be within these inclusive ranges; the frontend sliders use the same ones
# (EFFECT_OPTION_RANGES in frontend/src/utils/theme.ts).
EFFECT_OPTION_RANGES = {
    "brightness": (10, 100), "size": (10, 48), "speed": (1, 10), "count": (1, 10),
    # Floating emoji only. The angle is the direction of travel in degrees (0 = right, 90 = down);
    # the spin is in tenths of a turn per second, negative = counter-clockwise, 0 = none.
    "emoji_count": (3, 60), "emoji_angle": (0, 359), "emoji_spin": (-10, 10),
}
# Used for anything a profile hasn't set, and sent to clients so they never fill in gaps themselves.
DEFAULT_EFFECT_OPTIONS = {
    "brightness": 40, "size": 14, "speed": 4, "glow": False,
    # Bouncing DVD only:
    "count": 1, "color_change": True, "color": "#ffffff",
    # Matrix rain only:
    "rain_color": "#22ff66", "rain_rainbow": False, "rain_symbols": "katakana",
    # Floating emoji only (a tuple, so no request can end up sharing and changing one list):
    "emojis": ("🚀", "✨", "🔥", "💻", "🦄", "🍕"), "emoji_count": 14, "emoji_angle": 45,
    "emoji_path": "straight", "emoji_spin": 2,
}
BOOLEAN_EFFECT_OPTIONS = ("glow", "color_change", "rain_rainbow")
COLOR_EFFECT_OPTIONS = ("color", "rain_color")
# Options that must be one of a fixed set of names. The rain's characters themselves live in the
# frontend (RAIN_SYMBOLS in utils/theme.ts); "wave" and "bounce" are how the emoji move (FloatingEmoji.tsx).
RAIN_SYMBOL_SETS = ("katakana", "binary", "code", "chaos")
EMOJI_PATHS = ("straight", "wave", "bounce")
CHOICE_EFFECT_OPTIONS = {"rain_symbols": RAIN_SYMBOL_SETS, "emoji_path": EMOJI_PATHS}
# How many emoji a profile may list, and the longest one (a family or couple with skin tones is ~10 code points).
MAX_EMOJIS = 12
MAX_EMOJI_CODEPOINTS = 12
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
# The UI's text is light, so the card background has to be dark enough to keep it readable.
# 0.05 is WCAG relative luminance (0 = black, 1 = white); keep in sync with frontend/src/utils/theme.ts.
MAX_BACKGROUND_LUMINANCE = 0.05


class ValidationError(Exception):
    def __init__(self, fields: dict[str, str], message: str = "Invalid profile data.", conflict: bool = False):
        super().__init__(message)
        self.message = message
        self.fields = fields
        self.conflict = conflict


# ---------- reads ----------

def _profile_query():
    return Profile.query.options(selectinload(Profile.links), selectinload(Profile.projects))


def get_profile(profile_id: uuid.UUID) -> Profile | None:
    return _profile_query().filter(Profile.id == profile_id).one_or_none()


def get_demo_profile() -> Profile | None:
    email = current_app.config["DEMO_USER_EMAIL"]
    return _profile_query().join(User).filter(User.email == email).one_or_none()


def _lower_set(values: list[str]) -> set[str]:
    return {value.lower() for value in values}


def list_profiles(
    query: str = "",
    skills: list[str] | None = None,
    interests: list[str] | None = None,
    looking_for: list[str] | None = None,
    location: str = "",
    exclude_id: uuid.UUID | None = None,
) -> list[Profile]:
    """Filter in Python for now; move to SQL once the dataset grows."""
    profiles = _profile_query().order_by(Profile.created_at, Profile.username).all()
    query = query.strip().lower()
    location = location.strip().lower()
    wanted_skills = _lower_set(skills or [])
    wanted_interests = _lower_set(interests or [])
    wanted_looking_for = _lower_set(looking_for or [])

    results = []
    for profile in profiles:
        if exclude_id is not None and profile.id == exclude_id:
            continue
        # Every selected skill/interest must be present (filter chips narrow results).
        if wanted_skills and not wanted_skills <= _lower_set(profile.skills):
            continue
        if wanted_interests and not wanted_interests <= _lower_set(profile.interests):
            continue
        # "Looking for" matches ANY selected option: people only list a few, so requiring
        # all of them (e.g. both Mentor and Hackathon team) would hide almost everyone.
        if wanted_looking_for and wanted_looking_for.isdisjoint(_lower_set(profile.looking_for)):
            continue
        if location and location not in (profile.location or "").lower():
            continue
        if query and query not in _search_text(profile):
            continue
        results.append(profile)
    return results


def filter_options() -> dict[str, list[str]]:
    """Every value a profile may use for `skills` and `looking_for` (see `validate_update`).

    The Discover filter menu and the Edit Profile pickers both read this, so they can't drift
    from what the backend accepts.
    """
    return {
        "skills": sorted(ALL_TECHNOLOGIES, key=str.lower),
        "looking_for": list(LOOKING_FOR_OPTIONS),
    }


def _search_text(profile: Profile) -> str:
    parts = [
        profile.full_name,
        profile.username,
        profile.bio,
        profile.location or "",
        profile.education or "",
        profile.favorite_ide or "",
        profile.experience_level or "",
        *profile.skills,
        *profile.interests,
        *profile.favorite_ai_agents,
        *(project.title for project in profile.projects),
    ]
    return " ".join(parts).lower()


# ---------- serialization ----------

def _iso(value) -> str | None:
    return value.isoformat() if value else None


def to_dict(profile: Profile) -> dict[str, Any]:
    data = {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "full_name": profile.full_name,
        "username": profile.username,
        "avatar_url": (url_for("profiles.get_photo", profile_id=profile.id, v=hashlib.sha256(profile.user.photo_data).hexdigest()[:16], _external=True)
                       if profile.user.photo_data else profile.avatar_url),
        "location": profile.location,
        "education": profile.education,
        "bio": profile.bio,
        "favorite_ide": profile.favorite_ide,
        "favorite_ai_agents": list(profile.favorite_ai_agents),
        "skills": list(profile.skills),
        "interests": list(profile.interests),
        "experience_level": profile.experience_level,
        "looking_for": list(profile.looking_for),
        # Always an object so the frontend never has to null-check it; null = default look.
        "theme": {
            "background": (profile.theme or {}).get("background"),
            "effect": (profile.theme or {}).get("effect"),
            "effect_options": {**DEFAULT_EFFECT_OPTIONS, **(profile.theme or {}).get("effect_options", {})},
        },
        "links": [
            {"id": str(link.id), "label": link.label, "url": link.url} for link in profile.links
        ],
        "projects": [
            {
                "id": str(project.id),
                "title": project.title,
                "description": project.description,
                "project_url": project.project_url,
                "technologies": list(project.technologies),
            }
            for project in profile.projects
        ],
        "created_at": _iso(profile.created_at),
        "updated_at": _iso(profile.updated_at),
    }
    data["mog"] = compute_mog_score(data)
    return data


def apply_mog_filters(profiles: list[dict], min_tier: str = "", sort: str = "") -> list[dict]:
    """Keep profiles at or above `min_tier`; `sort="mog"` puts the biggest moggers first."""
    if min_tier:
        floor = tier_floor(min_tier)
        if floor is None:
            raise ValidationError({"min_tier": "Unknown tier."}, "Unknown Mog tier.")
        profiles = [p for p in profiles if p["mog"]["score"] >= floor]
    if sort == "mog":
        profiles = sorted(profiles, key=lambda p: p["mog"]["score"], reverse=True)
    elif sort:
        raise ValidationError({"sort": "Use 'mog' or leave it empty."}, "Unknown sort.")
    return profiles


# ---------- validation helpers ----------

def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _clean_string(value: Any, field: str, max_length: int, required: bool, errors: dict) -> str | None:
    if value is None:
        if required:
            errors[field] = "This field is required."
        return None
    if not isinstance(value, str):
        errors[field] = "Must be a string."
        return None
    value = value.strip()
    if required and not value:
        errors[field] = "This field is required."
        return None
    if len(value) > max_length:
        errors[field] = f"Must be at most {max_length} characters."
        return None
    return value or None


def _clean_tags(value: Any, field: str, max_items: int, errors: dict) -> list[str] | None:
    if not isinstance(value, list):
        errors[field] = "Must be a list of strings."
        return None
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            errors[field] = "Must be a list of strings."
            return None
        item = item.strip()
        if not item:
            continue
        if len(item) > MAX_TAG_LENGTH:
            errors[field] = f"Each item must be at most {MAX_TAG_LENGTH} characters."
            return None
        if item.lower() not in seen:  # drop case-insensitive duplicates, keep first spelling
            seen.add(item.lower())
            cleaned.append(item)
    if len(cleaned) > max_items:
        errors[field] = f"At most {max_items} items allowed."
        return None
    return cleaned


def _clean_links(value: Any, errors: dict) -> list[dict] | None:
    if not isinstance(value, list):
        errors["links"] = "Must be a list."
        return None
    if len(value) > MAX_LINKS:
        errors["links"] = f"At most {MAX_LINKS} links allowed."
        return None
    cleaned = []
    for index, item in enumerate(value):
        prefix = f"links[{index}]"
        if not isinstance(item, dict):
            errors[prefix] = "Must be an object with label and url."
            continue
        label = _clean_string(item.get("label"), f"{prefix}.label", 40, True, errors)
        url = _clean_string(item.get("url"), f"{prefix}.url", 500, True, errors)
        if url and not _is_http_url(url):
            errors[f"{prefix}.url"] = "Must be a valid http(s) URL."
            continue
        if label and url:
            cleaned.append({"label": label, "url": url})
    return cleaned


def _clean_technologies(values: list[str], field: str, errors: dict, noun: str = "technology") -> list[str]:
    """Map each value to its tech catalog spelling; report any that aren't recognized."""
    known: list[str] = []
    unknown: list[str] = []
    for value in values:
        canonical = normalize_technology(value)
        if canonical is None:
            unknown.append(value)
        elif canonical not in known:  # aliases can collapse ("js", "JavaScript") into one entry
            known.append(canonical)
    if unknown:
        errors[field] = (
            f"Unknown {noun}: {', '.join(unknown[:3])}{'…' if len(unknown) > 3 else ''}. "
            "Use a known language, framework or dev tool."
        )
    return known


def _clean_choices(values: list[str], field: str, allowed: tuple[str, ...], errors: dict) -> list[str]:
    """Map each value to its spelling in `allowed` (ignoring case); report any that aren't in it."""
    by_lower = {option.lower(): option for option in allowed}
    known = [by_lower[value.lower()] for value in values if value.lower() in by_lower]
    unknown = [value for value in values if value.lower() not in by_lower]
    if unknown:
        errors[field] = (
            f"Unknown option: {', '.join(unknown[:3])}{'…' if len(unknown) > 3 else ''}. "
            f"Choose from: {', '.join(allowed)}."
        )
    return known


def _relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance of '#rrggbb': 0 is black, 1 is white."""
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)


def _looks_like_emoji(text: str) -> bool:
    """A rough check, not a full emoji list: short, no ASCII, no letters/digits/spaces, and at least one symbol.

    That keeps words and markup out while still allowing flags, skin tones and joined emoji like 👩‍💻.
    Python's stdlib has no emoji data, and the picker only ever sends real emoji, so this is the safety net.
    """
    if not text or len(text) > MAX_EMOJI_CODEPOINTS:
        return False
    if any(ord(char) < 128 for char in text):
        return False
    categories = {unicodedata.category(char) for char in text}
    # Cf = the joiner and tag characters, Mn = variation selectors, Sk = skin tones.
    # Cn (unassigned) is allowed because emoji newer than this Python's Unicode data show up as Cn.
    return categories <= {"So", "Sk", "Cf", "Mn", "Cn"} and bool(categories & {"So", "Cn"})


def _clean_emojis(value: Any, field: str, errors: dict) -> list[str] | None:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_EMOJIS:
        errors[field] = f"Must be a list of 1 to {MAX_EMOJIS} emoji."
        return None
    cleaned: list[str] = []
    for item in value:
        item = item.strip() if isinstance(item, str) else item
        if not isinstance(item, str) or not _looks_like_emoji(item):
            errors[field] = "Every item must be an emoji."
            return None
        if item not in cleaned:  # a repeat would just make that emoji more common; drop it
            cleaned.append(item)
    return cleaned


def _clean_effect_options(value: Any, errors: dict) -> dict[str, Any]:
    """Validate the effect's tuning knobs; returns only the ones that were sent."""
    if not isinstance(value, dict):
        errors["theme.effect_options"] = "Must be an object."
        return {}

    cleaned: dict[str, Any] = {}
    for key, option in value.items():
        field = f"theme.effect_options.{key}"
        if key in EFFECT_OPTION_RANGES:
            low, high = EFFECT_OPTION_RANGES[key]
            # bool is a subclass of int in Python, so exclude it explicitly (True would pass as 1).
            if not isinstance(option, int) or isinstance(option, bool) or not low <= option <= high:
                errors[field] = f"Must be a whole number from {low} to {high}."
            else:
                cleaned[key] = option
        elif key in BOOLEAN_EFFECT_OPTIONS:
            if not isinstance(option, bool):
                errors[field] = "Must be true or false."
            else:
                cleaned[key] = option
        elif key in COLOR_EFFECT_OPTIONS:
            # Strict #rrggbb only, like the background: the frontend hands it straight to a canvas.
            if not isinstance(option, str) or not HEX_COLOR.fullmatch(option.strip()):
                errors[field] = "Must be a hex color like #ff00ff."
            else:
                cleaned[key] = option.strip().lower()
        elif key in CHOICE_EFFECT_OPTIONS:
            names = CHOICE_EFFECT_OPTIONS[key]
            if option not in names:  # also catches non-strings, which can't equal a name
                errors[field] = f"Must be one of: {', '.join(names)}."
            else:
                cleaned[key] = option
        elif key == "emojis":
            emojis = _clean_emojis(option, field, errors)
            if emojis is not None:
                cleaned[key] = emojis
        else:
            errors[field] = "Unknown effect option."
    return cleaned


def _clean_theme(value: Any, errors: dict) -> dict[str, Any]:
    """Return the theme to store: only options that are set, so `{}` (or null) means default."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors["theme"] = "Must be an object."
        return {}
    for key in value:
        if key not in THEME_FIELDS:
            errors[f"theme.{key}"] = "Unknown theme option."

    cleaned: dict[str, Any] = {}
    background = value.get("background")
    if background is not None:
        # Only a strict #rrggbb ever reaches the database, because the frontend puts this
        # value straight into a style attribute.
        if not isinstance(background, str) or not HEX_COLOR.fullmatch(background.strip()):
            errors["theme.background"] = "Must be a hex color like #172554."
        elif _relative_luminance(background.strip()) > MAX_BACKGROUND_LUMINANCE:
            errors["theme.background"] = "That color is too light for the text. Pick a darker one."
        else:
            cleaned["background"] = background.strip().lower()

    effect = value.get("effect")
    if effect is not None:
        if effect not in THEME_EFFECTS:  # also catches non-strings, which can't equal a name
            errors["theme.effect"] = f"Must be one of: {', '.join(THEME_EFFECTS)}."
        else:
            cleaned["effect"] = effect

    # Kept even while the effect is off, so someone can switch it off and on without retuning.
    if value.get("effect_options") is not None:
        options = _clean_effect_options(value["effect_options"], errors)
        if options:
            cleaned["effect_options"] = options
    return cleaned


def _clean_projects(value: Any, errors: dict) -> list[dict] | None:
    if not isinstance(value, list):
        errors["projects"] = "Must be a list."
        return None
    if len(value) > MAX_PROJECTS:
        errors["projects"] = f"At most {MAX_PROJECTS} projects allowed."
        return None
    cleaned = []
    for index, item in enumerate(value):
        prefix = f"projects[{index}]"
        if not isinstance(item, dict):
            errors[prefix] = "Must be an object."
            continue
        title = _clean_string(item.get("title"), f"{prefix}.title", 120, True, errors)
        description = _clean_string(item.get("description", ""), f"{prefix}.description", 2000, False, errors)
        project_url = _clean_string(item.get("project_url"), f"{prefix}.project_url", 500, False, errors)
        if project_url and not _is_http_url(project_url):
            errors[f"{prefix}.project_url"] = "Must be a valid http(s) URL."
        technologies = _clean_tags(item.get("technologies", []), f"{prefix}.technologies", 20, errors)
        if technologies:
            technologies = _clean_technologies(technologies, f"{prefix}.technologies", errors)
        cleaned.append(
            {
                "title": title,
                "description": description or "",
                "project_url": project_url,
                "technologies": technologies or [],
            }
        )
    return cleaned


def validate_update(data: Any) -> dict[str, Any]:
    """Return cleaned values for the fields present in `data`, or raise ValidationError."""
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")

    allowed = set(STRING_FIELDS) | set(LIST_FIELDS) | {"links", "projects", "theme"}
    errors: dict[str, str] = {}
    for key in data:
        if key not in allowed:
            errors[key] = "Unknown or read-only field."

    cleaned: dict[str, Any] = {}
    for field, (max_length, required) in STRING_FIELDS.items():
        if field in data:
            cleaned[field] = _clean_string(data[field], field, max_length, required, errors)
    for field, max_items in LIST_FIELDS.items():
        if field in data:
            cleaned[field] = _clean_tags(data[field], field, max_items, errors)
    if cleaned.get("skills"):
        cleaned["skills"] = _clean_technologies(cleaned["skills"], "skills", errors, noun="skill")
    if cleaned.get("looking_for"):
        cleaned["looking_for"] = _clean_choices(cleaned["looking_for"], "looking_for", LOOKING_FOR_OPTIONS, errors)
    if "links" in data:
        cleaned["links"] = _clean_links(data["links"], errors)
    if "projects" in data:
        cleaned["projects"] = _clean_projects(data["projects"], errors)
    if "theme" in data:
        cleaned["theme"] = _clean_theme(data["theme"], errors)

    username = cleaned.get("username")
    if username and not USERNAME_PATTERN.match(username):
        errors["username"] = "Use 3-40 letters, numbers, underscores or hyphens."
    level = cleaned.get("experience_level")
    if level and level not in EXPERIENCE_LEVELS:
        errors["experience_level"] = f"Must be one of: {', '.join(EXPERIENCE_LEVELS)}."
    avatar_url = cleaned.get("avatar_url")
    if avatar_url and not _is_http_url(avatar_url):
        errors["avatar_url"] = "Must be a valid http(s) URL."

    if errors:
        raise ValidationError(errors)
    return cleaned


# ---------- writes ----------

def update_profile(profile: Profile, data: Any, photo=None, extra_errors=None) -> Profile:
    errors = dict(extra_errors or {})
    try:
        cleaned = validate_update(data)
    except ValidationError as error:
        errors.update(error.fields)
        cleaned = {}
        if not error.fields:
            raise

    new_username = data.get("username") if isinstance(data, dict) else None
    new_username = new_username.strip() if isinstance(new_username, str) else None
    if new_username and new_username.lower() != profile.username.lower():
        taken = Profile.query.filter(
            db.func.lower(Profile.username) == new_username.lower(), Profile.id != profile.id
        ).first()
        if taken:
            errors["username"] = "That username is already taken."

    if errors:
        raise ValidationError(errors, conflict=bool(new_username and errors.get("username") == "That username is already taken."))
    if photo:
        profile.user.photo_data, profile.user.photo_mimetype = photo

    for field in STRING_FIELDS:
        if field in cleaned:
            value = cleaned[field]
            if field == "bio" and value is None:
                value = ""  # bio is NOT NULL; an emptied bio is stored as ""
            setattr(profile, field, value)
    for field in LIST_FIELDS:
        if field in cleaned:
            setattr(profile, field, cleaned[field])  # assign a new list so SQLAlchemy sees the change

    # The theme is replaced as a whole too; an empty one is stored as NULL (default look).
    if "theme" in cleaned:
        profile.theme = cleaned["theme"] or None

    # Links and projects are replaced as a whole: the edit form always sends the full list.
    if "links" in cleaned:
        profile.links = [
            ProfileLink(label=link["label"], url=link["url"], position=index)
            for index, link in enumerate(cleaned["links"])
        ]
    if "projects" in cleaned:
        profile.projects = [
            Project(position=index, **project) for index, project in enumerate(cleaned["projects"])
        ]

    db.session.commit()
    return profile
