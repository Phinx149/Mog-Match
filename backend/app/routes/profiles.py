import uuid
import json
from io import BytesIO
import warnings

from flask import Blueprint, abort, current_app, jsonify, request, send_file
from PIL import Image, UnidentifiedImageError

from ..services import auth_service, profile_service, swipe_service
from ..services.auth_service import current_profile_or_401
from ..services.profile_service import ValidationError
from ..services.connection_service import is_blocked

bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")


def _list_arg(name: str) -> list[str]:
    """Accept both ?skills=Rust,Go and ?skills=Rust&skills=Go."""
    values: list[str] = []
    for raw in request.args.getlist(name):
        values.extend(part.strip() for part in raw.split(",") if part.strip())
    return values


@bp.get("", strict_slashes=False)
def list_profiles():
    me = auth_service.current_profile()  # Discover hides me and people I swiped on
    profiles = profile_service.list_profiles(
        query=request.args.get("q", ""),
        skills=_list_arg("skills"),
        interests=_list_arg("interests"),
        looking_for=_list_arg("looking_for"),
        location=request.args.get("location", ""),
        exclude_id=me.id if me else None,
        hidden_ids=swipe_service.swiped_ids(me) if me else None,
    )
    try:
        results = profile_service.apply_mog_filters(
            [profile_service.to_dict(p) for p in profiles],
            min_tier=request.args.get("min_tier", "").strip(),
            sort=request.args.get("sort", "").strip(),
        )
    except ValidationError as error:
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), 400
    return jsonify({"profiles": results, "count": len(results)})


@bp.get("/filter-options")
def get_filter_options():
    return jsonify(profile_service.filter_options())


@bp.get("/me")
def get_my_profile():
    return jsonify(profile_service.to_dict(current_profile_or_401()))


@bp.get("/me/matches")
def get_my_matches():
    """Everyone I liked, ranked by how similar they are to me (Mog Match)."""
    matches = swipe_service.list_matches(current_profile_or_401())
    return jsonify({"matches": matches, "count": len(matches)})


@bp.patch("/me")
def update_my_profile():
    profile = current_profile_or_401()
    data = request.get_json(silent=True)
    photo = None
    errors = {}
    if request.mimetype == "multipart/form-data":
        try:
            data = json.loads(request.form.get("profile", "{}"))
        except ValueError:
            data = None
        upload = request.files.get("photo")
        if upload:
            max_bytes = current_app.config["MAX_PHOTO_BYTES"]
            raw = upload.read(max_bytes + 1)
            if len(raw) > max_bytes:
                errors["photo"] = f"Choose a photo smaller than {max_bytes // (1024 * 1024)} MB."
            else:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("error", Image.DecompressionBombWarning)
                        with Image.open(BytesIO(raw)) as image:
                            if image.format not in ("JPEG", "PNG", "WEBP"):
                                raise ValueError()
                            image.verify()
                            photo = (raw, Image.MIME[image.format])
                except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
                    errors["photo"] = "Choose a valid JPEG, PNG or WebP image."
    try:
        profile_service.update_profile(profile, data, photo=photo, extra_errors=errors)
    except ValidationError as error:
        status = 409 if error.conflict else 400
        return jsonify({"error": {"message": error.message, "fields": error.fields}}), status
    return jsonify(profile_service.to_dict(profile))


@bp.get("/<uuid:profile_id>/photo")
def get_photo(profile_id):
    me = auth_service.current_profile()
    if me and is_blocked(me.id, profile_id):
        abort(404)
    profile = profile_service.get_profile(profile_id)
    if profile is None or not profile.user.photo_data:
        abort(404)
    return send_file(BytesIO(profile.user.photo_data), mimetype=profile.user.photo_mimetype,
                     download_name="profile-photo", max_age=0)


@bp.get("/<uuid:profile_id>")
def get_profile(profile_id: uuid.UUID):
    me = auth_service.current_profile()
    if me and is_blocked(me.id, profile_id):
        abort(404, description="Profile not found.")
    profile = profile_service.get_profile(profile_id)
    if profile is None:
        abort(404, description="Profile not found.")
    return jsonify(profile_service.to_dict(profile))
