"""Username + password login. After a successful login Flask's `session` (a cookie signed with
SECRET_KEY, so the browser can't edit it) remembers the user id; that is who "me" is."""

import uuid
from functools import lru_cache
from typing import Any

from flask import abort, session
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Profile, User
from . import profile_service
from .profile_service import ValidationError

SESSION_KEY = "user_id"


class LoginError(Exception):
    pass


@lru_cache
def hash_password(password: str) -> str:
    """Cached so seeding many users with the same password hashes it once (hashing is slow on purpose)."""
    return generate_password_hash(password)


def validate_login(data: Any) -> tuple[str, str]:
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key not in ("username", "password")}
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not username.strip():
        errors["username"] = "Required."
    if not isinstance(password, str) or not password:
        errors["password"] = "Required."
    if errors:
        raise ValidationError(errors, "Enter your username and password.")
    return username.strip().lstrip("@"), password


def log_in(data: Any) -> Profile:
    username, password = validate_login(data)
    profile = Profile.query.filter(db.func.lower(Profile.username) == username.lower()).one_or_none()
    user = profile.user if profile else None
    # Same message for "no such user" and "wrong password", so usernames can't be probed.
    if user is None or not user.password_hash or not check_password_hash(user.password_hash, password):
        raise LoginError("Wrong username or password.")
    previous = current_profile()
    if previous:
        from .chat_service import disconnect_profile
        disconnect_profile(previous.id)
    session.clear()
    session[SESSION_KEY] = str(user.id)
    return profile


def log_out() -> None:
    previous = current_profile()
    if previous:
        from .chat_service import disconnect_profile
        disconnect_profile(previous.id)
    session.clear()


def change_password(profile: Profile, data: Any) -> None:
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key not in ("current_password", "new_password")}
    current, new = data.get("current_password"), data.get("new_password")
    if not isinstance(current, str) or not current:
        errors["current_password"] = "Enter your current password."
    elif not profile.user.password_hash or not check_password_hash(profile.user.password_hash, current):
        errors["current_password"] = "Current password is incorrect."
    if not isinstance(new, str) or not 8 <= len(new) <= 128 or not new.strip():
        errors["new_password"] = "Use 8–128 characters."
    elif new == current:
        errors["new_password"] = "Choose a different password."
    if errors:
        raise ValidationError(errors, "Couldn't change your password.")
    # Use a fresh salted hash; do not cache real account passwords.
    profile.user.password_hash = generate_password_hash(new)
    db.session.commit()


def current_profile() -> Profile | None:
    """The logged-in user's profile, or None when nobody is logged in."""
    raw_id = session.get(SESSION_KEY)
    if raw_id is None:
        return None
    try:
        user = db.session.get(User, uuid.UUID(raw_id))
    except ValueError:
        return None
    if user is None or user.profile is None:  # e.g. deleted by `flask seed --reset`
        return None
    return profile_service.get_profile(user.profile.id)


def current_profile_or_401() -> Profile:
    """Use in every "me" route. Identity comes from the signed session, never from the request body."""
    profile = current_profile()
    if profile is None:
        abort(401, description="Log in first.")
    return profile


def session_dict(profile: Profile | None) -> dict[str, Any]:
    if profile is None:
        return {"user": None}
    full = profile_service.to_dict(profile)
    return {"user": {key: full[key] for key in ("id", "full_name", "username", "avatar_url")}}
