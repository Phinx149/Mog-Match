"""Invites: ask someone I liked to connect. The invite is a row in the `invites` table; the
recipient's inbox is just a query for rows where they are the recipient."""

import uuid
from typing import Any

from ..extensions import db
from ..models import Invite, Profile, Swipe
from . import profile_service
from .profile_service import ValidationError
from .swipe_service import NotFoundError

MAX_MESSAGE_LENGTH = 280
RESPONSES = ("accepted", "declined")


class ConflictError(Exception):
    pass


# ---------- serialization ----------

def _person(profile: Profile) -> dict[str, Any]:
    """Just enough of a profile to show who an invite is from/to."""
    full = profile_service.to_dict(profile)
    return {key: full[key] for key in ("id", "full_name", "username", "avatar_url")}


def to_dict(invite: Invite) -> dict[str, Any]:
    return {
        "id": str(invite.id),
        "sender": _person(invite.sender),
        "recipient": _person(invite.recipient),
        "message": invite.message,
        "status": invite.status,
        "created_at": invite.created_at.isoformat(),
        "updated_at": invite.updated_at.isoformat(),
    }


# ---------- validation ----------

def validate_invite(data: Any) -> tuple[uuid.UUID, str | None]:
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key not in ("recipient_id", "message")}

    recipient_id = None
    try:
        recipient_id = uuid.UUID(str(data.get("recipient_id")))
    except ValueError:
        errors["recipient_id"] = "Must be a profile id."

    message = data.get("message")
    if message is not None and not isinstance(message, str):
        errors["message"] = "Must be text."
    elif isinstance(message, str):
        message = message.strip() or None  # an empty message is the same as no message
        if message and len(message) > MAX_MESSAGE_LENGTH:
            errors["message"] = f"Keep it under {MAX_MESSAGE_LENGTH} characters."

    if errors:
        raise ValidationError(errors, "Invalid invite.")
    return recipient_id, message


def validate_response(data: Any) -> str:
    if not isinstance(data, dict):
        raise ValidationError({}, "Request body must be a JSON object.")
    errors = {key: "Unknown field." for key in data if key != "status"}
    status = data.get("status")
    if status not in RESPONSES:
        errors["status"] = f"Must be one of: {', '.join(RESPONSES)}."
    if errors:
        raise ValidationError(errors, "Invalid response.")
    return status


# ---------- actions ----------

def send_invite(me: Profile, data: Any) -> dict[str, Any]:
    """Invite someone I liked. One invite per pair, so a repeat (either direction) is a conflict."""
    recipient_id, message = validate_invite(data)
    if recipient_id == me.id:
        raise ValidationError({"recipient_id": "You can't invite yourself."}, "Invalid invite.")
    recipient = profile_service.get_profile(recipient_id)
    if recipient is None:
        raise NotFoundError("Profile not found.")

    liked = Swipe.query.filter_by(swiper_id=me.id, target_id=recipient.id, action="like").first()
    if liked is None:
        raise ValidationError(
            {"recipient_id": "Like them on Discover first."}, "You can only invite people you've liked."
        )
    if Invite.query.filter_by(sender_id=me.id, recipient_id=recipient.id).first():
        raise ConflictError(f"You've already invited {recipient.full_name}.")
    if Invite.query.filter_by(sender_id=recipient.id, recipient_id=me.id).first():
        raise ConflictError(f"{recipient.full_name} already invited you. Check your inbox.")

    invite = Invite(sender_id=me.id, recipient_id=recipient.id, message=message, status="pending")
    db.session.add(invite)
    db.session.commit()
    return to_dict(invite)


def get_inbox(me: Profile) -> dict[str, Any]:
    """Invites sent to me and invites I sent, newest first."""
    newest_first = Invite.created_at.desc()
    received = Invite.query.filter_by(recipient_id=me.id).order_by(newest_first).all()
    sent = Invite.query.filter_by(sender_id=me.id).order_by(newest_first).all()
    return {
        "received": [to_dict(invite) for invite in received],
        "sent": [to_dict(invite) for invite in sent],
        "pending_count": sum(invite.status == "pending" for invite in received),
    }


def respond_to_invite(me: Profile, invite_id: uuid.UUID, data: Any) -> dict[str, Any]:
    """Accept or decline an invite. Only its recipient can, and only once."""
    status = validate_response(data)
    invite = db.session.get(Invite, invite_id)
    # Someone else's invite looks the same as a missing one, so ids can't be probed.
    if invite is None or invite.recipient_id != me.id:
        raise NotFoundError("Invite not found.")
    if invite.status != "pending":
        raise ConflictError(f"You already {invite.status} this invite.")
    invite.status = status
    db.session.commit()
    return to_dict(invite)


def cancel_invite(me: Profile, invite_id: uuid.UUID) -> None:
    """Take back an invite I sent, as long as they haven't answered it yet."""
    invite = db.session.get(Invite, invite_id)
    if invite is None or invite.sender_id != me.id:
        raise NotFoundError("Invite not found.")
    if invite.status != "pending":
        raise ConflictError(f"They already {invite.status} it, so it can't be cancelled.")
    db.session.delete(invite)
    db.session.commit()
