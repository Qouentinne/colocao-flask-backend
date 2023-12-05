import pytest
from sqlalchemy import text
from flaskr.app import create_app
from flaskr.db import db
from flaskr.api import create_api
from flaskr.models import BaseModel, Group, User

@pytest.fixture
def app():
    app = create_app("test", db_uri = 'sqlite://')
    app.config['TESTING'] = True

    db.init_app(app)
    
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text("ATTACH DATABASE ':memory:' AS public"))
        db.create_all()
        BaseModel.metadata.create_all(db.engine)

        test_group = Group(name = "test_group")
        user1 = User(username="user1", groups=[test_group])
        user2 = User(username="user2", groups=[test_group])
        user3= User(username="user3", groups=[test_group])
        
        db.session.add_all([test_group, user1, user2, user3])
        db.session.commit()
    
    yield app


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.app_context():        
        create_api(app)        
        yield app.test_client()

@pytest.fixture
def local_client(client, monkeypatch):
    with client:
        monkeypatch.setenv("ENVIRONMENT", "LOCAL")
        yield client

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
