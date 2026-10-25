from flask import Blueprint, abort, jsonify, request

from ..services import auth_service
from ..services.auth_service import LoginError
from ..services.profile_service import ValidationError

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def log_in():
    try:
        profile = auth_service.log_in(request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    except LoginError as error:
        abort(401, description=str(error))
    return jsonify(auth_service.session_dict(profile))


@bp.post("/signup")
def sign_up():
    try:
        profile = auth_service.sign_up(request.get_json(silent=True))
    except ValidationError as error:
        status = 409 if error.conflict else 400  # 409 = that username is taken
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), status
    return jsonify(auth_service.session_dict(profile)), 201


@bp.post("/logout")
def log_out():
    auth_service.log_out()
    return jsonify({"user": None})


@bp.get("/session")
def get_session():
    """Who am I? `{"user": null}` when logged out (not an error: the frontend shows the login page)."""
    return jsonify(auth_service.session_dict(auth_service.current_profile()))


@bp.patch("/password")
def change_password():
    profile = auth_service.current_profile_or_401()
    try:
        auth_service.change_password(profile, request.get_json(silent=True))
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    return jsonify({"ok": True})
