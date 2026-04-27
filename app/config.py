from __future__ import annotations

import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-lab-only-change-in-production")

    _default_sqlite = Path(__file__).resolve().parent.parent / "instance" / "lab.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + str(_default_sqlite),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_HEADERS = ["X-CSRFToken", "X-CSRF-Token"]
