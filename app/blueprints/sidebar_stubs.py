"""Placeholder HTML routes so global nav never points at `#` or missing URLs."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("sidebar_stubs", __name__)


@bp.get("/courses")
@login_required
def courses_stub():
    return render_template("courses_stub.html")


@bp.get("/reminders")
@login_required
def reminders_stub():
    return render_template("reminders_stub.html")


@bp.get("/preferences")
@login_required
def preferences_stub():
    return render_template("preferences_stub.html")
