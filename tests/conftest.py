from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app(tmp_path: Path):
    class TC(TestConfig):
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp_path / "test.db")

    application = create_app(TC)
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
