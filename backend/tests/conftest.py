import pytest

from app import create_app
from app.extensions import db
from app.seed import seed_database


@pytest.fixture
def app(tmp_path):
    db_path = (tmp_path / "test.db").as_posix()
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}"})
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()  # release the file so Windows can delete tmp_path


@pytest.fixture
def client(app):
    return app.test_client()
