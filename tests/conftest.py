import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.seed import seed_database


@pytest.fixture()
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def login(client, email="you@student.uwa.edu.au", password="password123"):
    return client.post(
        "/login",
        data={
            "form-name": "login",
            "login-email": email,
            "login-password": password,
        },
        follow_redirects=True,
    )


@pytest.fixture(name="login")
def login_fixture(client):
    def _login(email="you@student.uwa.edu.au", password="password123"):
        return client.post(
            "/login",
            data={
                "form-name": "login",
                "login-email": email,
                "login-password": password,
            },
            follow_redirects=True,
        )
    return _login
