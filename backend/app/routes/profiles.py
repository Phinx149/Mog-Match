import uuid
import json
from io import BytesIO
import warnings

from flask import Blueprint, abort, jsonify, request, send_file
from PIL import Image, UnidentifiedImageError

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
        looking_for=_list_arg("looking_for"),
        location=request.args.get("location", ""),
        exclude_id=demo.id if demo else None,
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
    return jsonify(profile_service.to_dict(_demo_profile_or_404()))


@bp.patch("/me")
def update_my_profile():
    profile = _demo_profile_or_404()
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
            raw = upload.read(5 * 1024 * 1024 + 1)
            if len(raw) > 5 * 1024 * 1024:
                errors["photo"] = "Choose a photo smaller than 5 MB."
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
    profile = profile_service.get_profile(profile_id)
    if profile is None or not profile.user.photo_data:
        abort(404)
    return send_file(BytesIO(profile.user.photo_data), mimetype=profile.user.photo_mimetype,
                     download_name="profile-photo", max_age=0)


@bp.get("/<uuid:profile_id>")
def get_profile(profile_id: uuid.UUID):
    profile = profile_service.get_profile(profile_id)
    if profile is None:
        abort(404, description="Profile not found.")
    return jsonify(profile_service.to_dict(profile))
