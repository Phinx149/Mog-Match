import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import DEFAULT_SECRET_KEY, Config
from .extensions import db, migrate


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False  # keep response fields in the order to_dict() defines them
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    if app.config["ON_VERCEL"]:
        _check_production_config(app)
        # Vercel's proxy terminates HTTPS; trust its X-Forwarded-* headers so photo URLs
        # (url_for(..., _external=True)) come out as https://<your-domain>/...
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        # Local dev only: a SQLite file in backend/instance/. (Vercel's disk is read-only.)
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, "mogmatch.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path.replace("\\", "/")

    db.init_app(app)
    migrate.init_app(app, db)
    # supports_credentials lets the frontend send the login cookie with its requests.
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)

    from . import models  # noqa: F401  (registers models with SQLAlchemy/Alembic)
    from .routes.auth import bp as auth_bp
    from .routes.health import bp as health_bp
    from .routes.invites import bp as invites_bp
    from .routes.profiles import bp as profiles_bp
    from .routes.swipes import bp as swipes_bp
    from .seed import register_commands

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(swipes_bp)
    app.register_blueprint(invites_bp)
    register_commands(app)
    _register_error_handlers(app)

    return app


def _check_production_config(app: Flask) -> None:
    """Fail the deploy loudly instead of running with a missing database or a guessable SECRET_KEY."""
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Set DATABASE_URL (Postgres) in the Vercel project's environment variables.")
    if app.config["SECRET_KEY"] == DEFAULT_SECRET_KEY:
        raise RuntimeError("Set SECRET_KEY to a long random string in the Vercel project's environment variables.")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify({"error": {"message": error.description}}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled error: %s", error)
        return jsonify({"error": {"message": "Internal server error"}}), 500
