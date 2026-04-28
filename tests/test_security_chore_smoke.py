"""Lightweight checks for the security chore (password hashing, CSRF when enabled)."""

from __future__ import annotations

import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import User


class CSRFOnConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True


@pytest.fixture()
def app_csrf_on(tmp_path):
    class TC(CSRFOnConfig):
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "csrf.db")

    application = create_app(TC)
    yield application


def test_seed_user_password_is_not_stored_plaintext(app):
    with app.app_context():
        u = User.query.filter_by(email="alice@lab.local").first()
        assert u is not None
        assert u.password_hash != "labdemo123"
        assert u.password_hash.startswith("pbkdf2:") or u.password_hash.startswith("scrypt:")


def test_login_post_rejects_missing_csrf_when_csrf_enabled(app_csrf_on):
    client = app_csrf_on.test_client()
    rv = client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=False,
    )
    assert rv.status_code == 400
