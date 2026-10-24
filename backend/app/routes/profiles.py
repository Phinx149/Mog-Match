import uuid

from flask import Blueprint, abort, jsonify, request

from ..services import profile_service
from ..services.profile_service import ValidationError

bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")


def _list_arg(name: str) -> list[str]:
    """Accept both ?skills=Rust,Go and ?skills=Rust&skills=Go."""
    values: list[str] = []
    for raw in request.args.getlist(name):
        values.extend(part.strip() for part in raw.split(",") if part.strip())
    return values


def _demo_profile_or_404():
    profile = profile_service.get_demo_profile()
    if profile is None:
        abort(404, description="Demo profile not found. Run `flask seed` in the backend folder.")
    return profile


@bp.get("", strict_slashes=False)
def list_profiles():
    demo = profile_service.get_demo_profile()
    profiles = profile_service.list_profiles(
        query=request.args.get("q", ""),
        skills=_list_arg("skills"),
        interests=_list_arg("interests"),
        location=request.args.get("location", ""),
        exclude_id=demo.id if demo else None,
    )
    return jsonify(
        {"profiles": [profile_service.to_dict(p) for p in profiles], "count": len(profiles)}
    )


@bp.get("/me")
def get_my_profile():
    return jsonify(profile_service.to_dict(_demo_profile_or_404()))


@bp.patch("/me")
def update_my_profile():
    profile = _demo_profile_or_404()
    data = request.get_json(silent=True)
    try:
        profile_service.update_profile(profile, data)
    except ValidationError as error:
        status = 409 if error.conflict else 400
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), status
    return jsonify(profile_service.to_dict(profile))


@bp.get("/<uuid:profile_id>")
def get_profile(profile_id: uuid.UUID):
    profile = profile_service.get_profile(profile_id)
    if profile is None:
        abort(404, description="Profile not found.")
    return jsonify(profile_service.to_dict(profile))
