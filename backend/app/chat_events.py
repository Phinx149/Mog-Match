from flask import current_app
from flask_socketio import join_room
from werkzeug.exceptions import HTTPException

from .extensions import db, socketio
from .services.auth_service import current_profile
from .services.chat_service import send_message, user_room
from .services.profile_service import ValidationError


def register_events():
    @socketio.on("connect")
    def connect(auth=None):
        me = current_profile()
        if me is None:
            return False
        join_room(user_room(me.id))

    @socketio.on("chat:send")
    def send(data):
        me = current_profile()
        if me is None:
            return {"error": "Log in first.", "status": 401}
        try:
            return {"message": send_message(me, data)}
        except ValidationError as error:
            return {"error": error.message, "fields": error.fields, "status": 400}
        except HTTPException as error:
            return {"error": error.description, "status": error.code}
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Chat send failed")
            return {"error": "Message could not be saved. Please retry.", "status": 500}
