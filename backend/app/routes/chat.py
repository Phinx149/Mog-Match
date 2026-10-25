from flask import Blueprint, jsonify, request

from ..services.auth_service import current_profile_or_401
from ..services import chat_service, idea_service, studio_service
from ..services.profile_service import ValidationError

bp = Blueprint("chat", __name__, url_prefix="/api/conversations")


@bp.get("")
def conversations():
    return jsonify({"conversations": chat_service.list_conversations(current_profile_or_401())})


@bp.get("/<uuid:invite_id>/messages")
def messages(invite_id):
    return jsonify(chat_service.history(current_profile_or_401(), invite_id, request.args.get("before")))


@bp.post("/<uuid:invite_id>/read")
def mark_read(invite_id):
    chat_service.mark_read(current_profile_or_401(), invite_id, request.get_json(silent=True))
    return jsonify({"ok": True})


@bp.get("/<uuid:invite_id>/ideas")
def ideas(invite_id):
    return jsonify({"ideas": chat_service.ideas(current_profile_or_401(), invite_id)})


@bp.post("/<uuid:invite_id>/ideas")
def generate(invite_id):
    try:
        idea = idea_service.generate(current_profile_or_401(), invite_id, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    return jsonify(idea), 201


@bp.get("/<uuid:invite_id>/ideas/<uuid:idea_id>/assistant")
def studio_history(invite_id, idea_id):
    return jsonify(studio_service.history(current_profile_or_401(), invite_id, idea_id, request.args.get("before")))


@bp.post("/<uuid:invite_id>/ideas/<uuid:idea_id>/assistant")
def studio_ask(invite_id, idea_id):
    try:
        turn = studio_service.ask(current_profile_or_401(), invite_id, idea_id, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    return jsonify(turn), 201


@bp.post("/<uuid:invite_id>/ideas/<uuid:idea_id>/assistant/<int:turn_id>/apply")
def studio_apply(invite_id, idea_id, turn_id):
    result, created = studio_service.apply(current_profile_or_401(), invite_id, idea_id, turn_id)
    return jsonify(result), 201 if created else 200
