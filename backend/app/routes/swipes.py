from flask import Blueprint, abort, jsonify, request

from ..services import swipe_service
from ..services.auth_service import current_profile_or_401
from ..services.profile_service import ValidationError
from ..services.swipe_service import NotFoundError

bp = Blueprint("swipes", __name__, url_prefix="/api/swipes")


@bp.post("", strict_slashes=False)
def create_swipe():
    me = current_profile_or_401()
    try:
        result = swipe_service.record_swipe(me, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    except NotFoundError as error:
        abort(404, description=str(error))
    return jsonify(result), 201


@bp.delete("/<uuid:target_id>")
def remove_swipe(target_id):
    """Unlike (or un-pass) one person, so they show up on Discover again."""
    try:
        swipe_service.remove_swipe(current_profile_or_401(), target_id)
    except NotFoundError as error:
        abort(404, description=str(error))
    return jsonify({"removed": True})


@bp.delete("", strict_slashes=False)
def clear_swipes():
    """Forget all my likes/passes, so Discover shows everyone again."""
    removed = swipe_service.clear_swipes(current_profile_or_401())
    return jsonify({"removed": removed})
