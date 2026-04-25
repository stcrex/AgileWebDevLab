from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__)


@bp.get("/login")
def login_page():
    if request.args.get("next"):
        pass
    return render_template("login.html")


@bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.login_page"))
    login_user(user, remember=True)
    nxt = request.args.get("next") or url_for("exams.exams_list")
    return redirect(nxt)


@bp.post("/logout")
@login_required
def logout_post():
    logout_user()
    return redirect(url_for("auth.login_page"))
