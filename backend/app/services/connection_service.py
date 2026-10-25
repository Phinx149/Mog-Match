"""Connection lifecycle and pair-wide blocking, independent of chat transport."""

from flask import abort
from sqlalchemy import and_, or_

from ..extensions import db
from ..models import Invite, Swipe, UserBlock
from ..models.base import utcnow


def pair_filter(model, first, second, left="sender_id", right="recipient_id"):
    a, b = getattr(model, left), getattr(model, right)
    return or_(and_(a == first, b == second), and_(a == second, b == first))


def blocked_ids(profile_id):
    blocks = UserBlock.query.filter(or_(UserBlock.blocker_id == profile_id,
                                        UserBlock.blocked_id == profile_id)).all()
    return {row.blocked_id if row.blocker_id == profile_id else row.blocker_id for row in blocks}


def is_blocked(first, second):
    return UserBlock.query.filter(pair_filter(UserBlock, first, second, "blocker_id", "blocked_id")).first() is not None


def end_connection(me, invite_id, *, block=False):
    invite = Invite.query.filter_by(id=invite_id).populate_existing().with_for_update().first()
    if invite is None or me.id not in (invite.sender_id, invite.recipient_id):
        abort(404, description="Conversation not found.")
    other_id = invite.recipient_id if me.id == invite.sender_id else invite.sender_id
    if is_blocked(me.id, other_id):
        abort(404, description="Conversation not found.")
    if invite.status != "accepted":
        abort(409, description="Only an active match can be unmatched or blocked.")
    invite.status = "unmatched"
    invite.unmatched_at = utcnow()
    Swipe.query.filter(pair_filter(Swipe, me.id, other_id, "swiper_id", "target_id")).delete(synchronize_session=False)
    if block:
        db.session.add(UserBlock(blocker_id=me.id, blocked_id=other_id))
    db.session.commit()
    from .chat_service import notify
    # No block reason or identity is broadcast to the other participant.
    notify(invite, "connection:updated")
    notify(invite)
