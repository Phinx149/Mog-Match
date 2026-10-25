from flask import Blueprint, abort, jsonify, request

from ..services import invite_service
from ..services.auth_service import current_profile_or_401
from ..services.invite_service import ConflictError
from ..services.profile_service import ValidationError
from ..services.swipe_service import NotFoundError

bp = Blueprint("invites", __name__, url_prefix="/api/invites")


@bp.post("", strict_slashes=False)
def send_invite():
    try:
        invite = invite_service.send_invite(current_profile_or_401(), request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    except NotFoundError as error:
        abort(404, description=str(error))
    except ConflictError as error:
        abort(409, description=str(error))
    return jsonify(invite), 201


@bp.get("/inbox")
def get_inbox():
    return jsonify(invite_service.get_inbox(current_profile_or_401()))


@bp.patch("/<uuid:invite_id>")
def respond_to_invite(invite_id):
    """Accept or decline an invite sent to me."""
    try:
        invite = invite_service.respond_to_invite(
            current_profile_or_401(), invite_id, request.get_json(silent=True)
        )
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    except NotFoundError as error:
        abort(404, description=str(error))
    except ConflictError as error:
        abort(409, description=str(error))
    return jsonify(invite)


@bp.delete("/<uuid:invite_id>")
def cancel_invite(invite_id):
    """Take back an invite I sent that hasn't been answered yet."""
    try:
        invite_service.cancel_invite(current_profile_or_401(), invite_id)
    except NotFoundError as error:
        abort(404, description=str(error))
    except ConflictError as error:
        abort(409, description=str(error))
    return jsonify({"removed": True})
