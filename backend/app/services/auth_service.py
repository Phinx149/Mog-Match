"""Username + password sign-up and login. After either one Flask's `session` (a cookie signed with
SECRET_KEY, so the browser can't edit it) remembers the user id; that is who "me" is."""

import uuid
from functools import lru_cache
from typing import Any

from flask import abort, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import Profile, User
from . import profile_service
from .profile_service import ValidationError

SESSION_KEY = "user_id"
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128  # hashing is slow on purpose, so don't let anyone make us hash a megabyte
USERNAME_TAKEN = "That username is already taken."


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
    _start_session(user)
    return profile


def validate_sign_up(data: Any) -> dict[str, str]:
    """Return cleaned `full_name`, `username` and `password`, or raise ValidationError.
    Name and username go through the same rules as the profile editor, so they can't disagree."""
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key not in ("full_name", "username", "password")}
    try:
        cleaned = profile_service.validate_update(
            {"full_name": data.get("full_name"), "username": data.get("username")}
        )
    except ValidationError as error:
        errors.update(error.fields)
        cleaned = {}

    password = data.get("password")
    if not isinstance(password, str) or not password:
        errors["password"] = "This field is required."
    elif len(password) < MIN_PASSWORD_LENGTH:
        errors["password"] = f"Use at least {MIN_PASSWORD_LENGTH} characters."
    elif len(password) > MAX_PASSWORD_LENGTH:
        errors["password"] = f"Must be at most {MAX_PASSWORD_LENGTH} characters."

    if errors:
        raise ValidationError(errors, "Fix the highlighted fields.")
    return {**cleaned, "password": password}


def sign_up(data: Any) -> Profile:
    """Create a new account (a user and an almost empty profile) and log it in.
    The profile is filled in afterwards on the edit-profile page."""
    cleaned = validate_sign_up(data)
    username = cleaned["username"]
    taken = Profile.query.filter(db.func.lower(Profile.username) == username.lower()).first()
    if taken:
        raise ValidationError({"username": USERNAME_TAKEN}, USERNAME_TAKEN, conflict=True)

    user = User(password_hash=generate_password_hash(cleaned["password"]))
    profile = Profile(user=user, full_name=cleaned["full_name"], username=username)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        # Someone grabbed the same username between our check and the insert (the column is unique).
        db.session.rollback()
        raise ValidationError({"username": USERNAME_TAKEN}, USERNAME_TAKEN, conflict=True) from None
    _start_session(user)
    return profile


def _start_session(user: User) -> None:
    """Remember `user` as "me", dropping whoever this browser was logged in as before."""
    previous = current_profile()
    if previous:
        from .chat_service import disconnect_profile
        disconnect_profile(previous.id)
    session.clear()
    session[SESSION_KEY] = str(user.id)


def log_out() -> None:
    previous = current_profile()
    if previous:
        from .chat_service import disconnect_profile
        disconnect_profile(previous.id)
    session.clear()


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
