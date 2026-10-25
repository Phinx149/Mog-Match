"""Likes/passes. Everyone I like becomes one of my matches, scored by how similar they are to
me (see mog_match.py). Passes are saved too, so Discover doesn't show those people again."""

import uuid
from typing import Any

from ..extensions import db
from ..models import Profile, Swipe
from . import profile_service
from .mog_match import compute_match, rank_matches
from .profile_service import ValidationError

ACTIONS = ("like", "pass")


class NotFoundError(Exception):
    pass


def validate_swipe(data: Any) -> tuple[uuid.UUID, str]:
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key not in ("target_id", "action")}

    target_id = None
    try:
        target_id = uuid.UUID(str(data.get("target_id")))
    except ValueError:
        errors["target_id"] = "Must be a profile id."
    action = data.get("action")
    if action not in ACTIONS:
        errors["action"] = f"Must be one of: {', '.join(ACTIONS)}."

    if errors:
        raise ValidationError(errors, "Invalid swipe.")
    return target_id, action


def record_swipe(me: Profile, data: Any) -> dict[str, Any]:
    """Save my like/pass (swiping again overwrites it). A like comes back with its match score."""
    target_id, action = validate_swipe(data)
    if target_id == me.id:
        raise ValidationError({"target_id": "You can't swipe on yourself."}, "Invalid swipe.")
    target = profile_service.get_profile(target_id)
    if target is None:
        raise NotFoundError("Profile not found.")

    swipe = Swipe.query.filter_by(swiper_id=me.id, target_id=target.id).one_or_none()
    if swipe is None:
        swipe = Swipe(swiper_id=me.id, target_id=target.id)
        db.session.add(swipe)
    swipe.action = action
    db.session.commit()

    match = None
    if action == "like":
        match = compute_match(profile_service.to_dict(me), profile_service.to_dict(target))
    return {"target_id": str(target.id), "action": action, "match": match}


def swiped_ids(me: Profile) -> set[uuid.UUID]:
    """Everyone I've already liked or passed, so Discover can hide them."""
    return {row.target_id for row in Swipe.query.filter_by(swiper_id=me.id)}


def list_matches(me: Profile) -> list[dict]:
    """Everyone I liked, most similar to me first."""
    liked = Swipe.query.filter_by(swiper_id=me.id, action="like").all()
    others = [profile_service.to_dict(swipe.target) for swipe in liked]
    # Sort by name first so ties in the match score come out in a stable order.
    others.sort(key=lambda p: p["full_name"].lower())
    return rank_matches(profile_service.to_dict(me), others)


def remove_swipe(me: Profile, target_id: uuid.UUID) -> None:
    """Undo my like/pass on one person: they leave my matches and come back to Discover."""
    swipe = Swipe.query.filter_by(swiper_id=me.id, target_id=target_id).one_or_none()
    if swipe is None:
        raise NotFoundError("You haven't liked or passed on this profile.")
    db.session.delete(swipe)
    db.session.commit()


def clear_swipes(me: Profile) -> int:
    """Forget all my likes/passes (Discover's "start over"). Returns how many were removed."""
    removed = Swipe.query.filter_by(swiper_id=me.id).delete()
    db.session.commit()
    return removed
