import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-lab-only-change-in-production")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(
        Path(__file__).resolve().parent.parent / "instance" / "lab.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_HEADERS = ["X-CSRFToken", "X-CSRF-Token"]
