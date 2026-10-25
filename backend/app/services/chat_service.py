"""An accepted invite is a private, persistent conversation between its two participants."""

import uuid
from datetime import timezone

from flask import abort
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ..extensions import db, socketio
from ..models import ChatMessage, Invite, ProjectIdea
from .invite_service import _person
from .profile_service import ValidationError

MAX_MESSAGE_LENGTH = 2000
PAGE_SIZE = 50


def timestamp(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.isoformat()


def user_room(profile_id):
    return f"profile:{profile_id}"


def disconnect_profile(profile_id):
    # Cookie sessions are snapshotted at the WebSocket handshake. Revoke existing sockets
    # on logout/account switch, so they cannot keep using an old authenticated session.
    for sid, _ in list(socketio.server.manager.get_participants("/", user_room(profile_id))):
        socketio.server.disconnect(sid, namespace="/")


def notify(invite, event="inbox:updated", payload=None):
    for profile_id in (invite.sender_id, invite.recipient_id):
        socketio.emit(event, payload or {"conversation_id": str(invite.id)}, to=user_room(profile_id))


def conversation(me, invite_id):
    try:
        invite_id = uuid.UUID(str(invite_id))
    except (ValueError, TypeError):
        abort(404, description="Conversation not found.")
    invite = db.session.get(Invite, invite_id)
    if invite is None or me.id not in (invite.sender_id, invite.recipient_id) or invite.status != "accepted":
        abort(404, description="Conversation not found.")
    return invite


def message_dict(message):
    return {"id": message.id, "conversation_id": str(message.invite_id),
            "sender_id": str(message.sender_id), "body": message.body,
            "client_token": message.client_token, "created_at": timestamp(message.created_at)}


def idea_dict(idea):
    return {"id": str(idea.id), "conversation_id": str(idea.invite_id),
            "generated_by": str(idea.generated_by), "brief": idea.brief, "content": idea.content,
            "context_message_id": idea.context_message_id, "created_at": timestamp(idea.created_at),
            "parent_idea_id": str(idea.parent_idea_id) if idea.parent_idea_id else None}


def conversation_dict(invite, me):
    other = invite.recipient if me.id == invite.sender_id else invite.sender
    latest = ChatMessage.query.filter_by(invite_id=invite.id).order_by(ChatMessage.id.desc()).first()
    read_id = invite.sender_read_id if me.id == invite.sender_id else invite.recipient_read_id
    unread = ChatMessage.query.filter(ChatMessage.invite_id == invite.id,
                                     ChatMessage.sender_id != me.id, ChatMessage.id > read_id).count()
    return {"id": str(invite.id), "person": _person(other), "opening_message": invite.message,
            "last_message": message_dict(latest) if latest else None, "unread_count": unread,
            "updated_at": timestamp(latest.created_at if latest else invite.updated_at)}


def list_conversations(me):
    invites = Invite.query.filter(Invite.status == "accepted", or_(Invite.sender_id == me.id,
                                                                   Invite.recipient_id == me.id)).all()
    return sorted([conversation_dict(invite, me) for invite in invites],
                  key=lambda row: row["updated_at"], reverse=True)


def history(me, invite_id, before=None):
    invite = conversation(me, invite_id)
    query = ChatMessage.query.filter_by(invite_id=invite.id)
    if before is not None:
        try:
            before = int(before)
            assert before > 0
        except (ValueError, TypeError, AssertionError):
            abort(400, description="Invalid message cursor.")
        query = query.filter(ChatMessage.id < before)
    rows = query.order_by(ChatMessage.id.desc()).limit(PAGE_SIZE + 1).all()
    return {"messages": [message_dict(row) for row in reversed(rows[:PAGE_SIZE])],
            "has_more": len(rows) > PAGE_SIZE}


def send_message(me, data):
    if not isinstance(data, dict):
        raise ValidationError({}, "Message must be an object.")
    errors = {key: "Unknown field." for key in data if key not in ("conversation_id", "body", "client_token")}
    body = data.get("body")
    if not isinstance(body, str) or not body.strip() or len(body) > MAX_MESSAGE_LENGTH:
        errors["body"] = f"Enter a message between 1 and {MAX_MESSAGE_LENGTH} characters."
    try:
        token = str(uuid.UUID(str(data.get("client_token"))))
    except (ValueError, TypeError):
        errors["client_token"] = "A unique message token is required."
    if errors:
        raise ValidationError(errors, "Couldn't send message.")
    invite = conversation(me, data.get("conversation_id"))
    existing = ChatMessage.query.filter_by(invite_id=invite.id, sender_id=me.id, client_token=token).first()
    if existing:
        return message_dict(existing)
    message = ChatMessage(invite_id=invite.id, sender_id=me.id, client_token=token, body=body.strip())
    db.session.add(message)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        existing = ChatMessage.query.filter_by(invite_id=invite.id, sender_id=me.id, client_token=token).first()
        if existing:
            return message_dict(existing)
        raise
    result = message_dict(message)
    notify(invite, "chat:message", result)
    return result


def mark_read(me, invite_id, data):
    invite = conversation(me, invite_id)
    last_id = data.get("message_id") if isinstance(data, dict) else None
    if type(last_id) is not int or not ChatMessage.query.filter_by(id=last_id, invite_id=invite.id).first():
        abort(400, description="Invalid message id.")
    key = "sender_read_id" if me.id == invite.sender_id else "recipient_read_id"
    # Never move the cursor backwards when requests from multiple tabs arrive out of order.
    db.session.query(Invite).filter(Invite.id == invite.id, getattr(Invite, key) < last_id).update(
        {key: last_id}, synchronize_session=False)
    db.session.commit()
    socketio.emit("chat:read", {"conversation_id": str(invite.id)}, to=user_room(me.id))


def ideas(me, invite_id):
    invite = conversation(me, invite_id)
    return [idea_dict(row) for row in ProjectIdea.query.filter_by(invite_id=invite.id)
            .order_by(ProjectIdea.created_at.desc()).all()]
