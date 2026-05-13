from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..forms import ForgotPasswordForm, LoginForm, LogoutForm, RegisterForm
from ..models import User

auth_bp = Blueprint("auth", __name__)


def _create_user_from_form(register_form: RegisterForm) -> User | None:
    """Create a user from a valid registration form, or flash an error."""
    email = register_form.email.data.lower().strip()
    if User.query.filter_by(email=email).first():
        flash("That email is already registered.", "danger")
        return None

    user = User(
        name=register_form.name.data.strip(),
        uwa_id=register_form.uwa_id.data.strip(),
        email=email,
    )
    user.set_password(register_form.password.data)
    db.session.add(user)
    db.session.commit()
    return user


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Dedicated login page.

    The template still includes a small registration tab so new users can create
    an account from the same screen during a demo.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.timetable"))

    login_form = LoginForm(prefix="login")
    register_form = RegisterForm(prefix="register")

    if request.method == "POST" and request.form.get("form-name") == "login" and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data.lower().strip()).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            flash("Welcome back to StudySync.", "success")
            return redirect(request.args.get("next") or url_for("main.timetable"))
        flash("Invalid email or password.", "danger")

    if request.method == "POST" and request.form.get("form-name") == "register" and register_form.validate_on_submit():
        user = _create_user_from_form(register_form)
        if user:
            login_user(user)
            flash("Account created. Start planning your week!", "success")
            return redirect(url_for("main.timetable"))

    return render_template("auth/login.html", login_form=login_form, register_form=register_form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Separate create-account page for a cleaner authentication flow."""
    if current_user.is_authenticated:
        return redirect(url_for("main.timetable"))

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = _create_user_from_form(register_form)
        if user:
            login_user(user)
            flash("Account created. Start planning your week!", "success")
            return redirect(url_for("main.timetable"))

    return render_template("auth/register.html", register_form=register_form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Demo password-reset page.

    In a production app this would email a secure reset token. For this
    university project demo it records the request and shows safe next steps
    without exposing whether the email exists.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.timetable"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash("Demo mode: if that student email exists, a production app would send a reset link. In this project build, please contact the project owner to reset access manually.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout confirmation page.

    GET shows a proper logout page. POST performs the logout using a CSRF-
    protected form, which avoids logging users out through a plain link.
    """
    logout_form = LogoutForm()
    if logout_form.validate_on_submit():
        logout_user()
        flash("You have been logged out safely.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/logout.html", logout_form=logout_form)
