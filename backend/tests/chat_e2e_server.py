"""Disposable browser-test server. Uses a temporary DB and a stub provider; never the real DB/key."""

import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db, socketio
from app.seed import seed_database, seed_test_users
from app.services import idea_service, studio_service


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="mogmatch-chat-e2e-") as folder:
        app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///" + Path(folder, "test.db").as_posix(),
                          "TESTING": True, "OPENAI_API_KEY": "browser-test-stub", "SEED_PASSWORD": "mogmatch-demo",
                          "CORS_ORIGINS": ["http://127.0.0.1:5174"]})
        with app.app_context():
            db.create_all(); seed_database(); seed_test_users()
        plan = json.loads(Path(__file__).with_name("fixtures").joinpath("project_plan.json").read_text())
        idea_service.request_plan = lambda context: plan
        def studio_reply(context):
            if context["mode"] == "ask":
                return studio_service.StudioReply(
                    answer=f"React and Flask fit both developers' skills in {context['selected_document']['title']}. A single service keeps deployment small.",
                    change_summary=[], proposal=None)
            revised = {**context["selected_document"], "title": "StudySprint Weekend",
                       "features": ["Create a study goal", "Track session completion"],
                       "architecture": "A single Flask service serves the React client and stores study goals in SQLite."}
            return studio_service.StudioReply(answer="Here is a smaller weekend MVP preview. The saved document is unchanged until you apply it.",
                change_summary=["Reduce the MVP to two core features.", "Use a single deployment."],
                proposal=idea_service.DesignDocument.model_validate(revised))
        studio_service.request_reply = studio_reply
        socketio.run(app, host="127.0.0.1", port=5002, allow_unsafe_werkzeug=True)
