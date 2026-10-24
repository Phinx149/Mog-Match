"""Profile reads, filtering, serialization and validated updates."""

import re
import uuid
from typing import Any
from urllib.parse import urlparse

from flask import current_app
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Profile, ProfileLink, Project, User

EXPERIENCE_LEVELS = ("Student", "Junior", "Mid-level", "Senior", "Lead")
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
    location: str = "",
    exclude_id: uuid.UUID | None = None,
) -> list[Profile]:
    """Filter in Python for now; move to SQL once the dataset grows."""
    profiles = _profile_query().order_by(Profile.created_at, Profile.username).all()
    query = query.strip().lower()
    location = location.strip().lower()
    wanted_skills = _lower_set(skills or [])
    wanted_interests = _lower_set(interests or [])

    results = []
    for profile in profiles:
        if exclude_id is not None and profile.id == exclude_id:
            continue
        # Every selected skill/interest must be present (filter chips narrow results).
        if wanted_skills and not wanted_skills <= _lower_set(profile.skills):
            continue
        if wanted_interests and not wanted_interests <= _lower_set(profile.interests):
            continue
        if location and location not in (profile.location or "").lower():
            continue
        if query and query not in _search_text(profile):
            continue
        results.append(profile)
    return results


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
    return {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "full_name": profile.full_name,
        "username": profile.username,
        "avatar_url": profile.avatar_url,
        "location": profile.location,
        "education": profile.education,
        "bio": profile.bio,
        "favorite_ide": profile.favorite_ide,
        "favorite_ai_agents": list(profile.favorite_ai_agents),
        "skills": list(profile.skills),
        "interests": list(profile.interests),
        "experience_level": profile.experience_level,
        "looking_for": list(profile.looking_for),
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

    allowed = set(STRING_FIELDS) | set(LIST_FIELDS) | {"links", "projects"}
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
    if "links" in data:
        cleaned["links"] = _clean_links(data["links"], errors)
    if "projects" in data:
        cleaned["projects"] = _clean_projects(data["projects"], errors)

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

def update_profile(profile: Profile, data: Any) -> Profile:
    cleaned = validate_update(data)

    new_username = cleaned.get("username")
    if new_username and new_username.lower() != profile.username.lower():
        taken = Profile.query.filter(
            db.func.lower(Profile.username) == new_username.lower(), Profile.id != profile.id
        ).first()
        if taken:
            raise ValidationError({"username": "That username is already taken."}, "Username taken.", conflict=True)

    for field in STRING_FIELDS:
        if field in cleaned:
            value = cleaned[field]
            if field == "bio" and value is None:
                value = ""  # bio is NOT NULL; an emptied bio is stored as ""
            setattr(profile, field, value)
    for field in LIST_FIELDS:
        if field in cleaned:
            setattr(profile, field, cleaned[field])  # assign a new list so SQLAlchemy sees the change

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
