import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import Config
from .extensions import db, migrate


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False  # keep response fields in the order to_dict() defines them
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, "mogmatch.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path.replace("\\", "/")

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from . import models  # noqa: F401  (registers models with SQLAlchemy/Alembic)
    from .routes.health import bp as health_bp
    from .routes.invites import bp as invites_bp
    from .routes.profiles import bp as profiles_bp
    from .routes.swipes import bp as swipes_bp
    from .seed import register_commands

    app.register_blueprint(health_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(swipes_bp)
    app.register_blueprint(invites_bp)
    register_commands(app)
    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify({"error": {"message": error.description}}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled error: %s", error)
        return jsonify({"error": {"message": "Internal server error"}}), 500
