from flask import Blueprint, flash, redirect, render_template_string, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - StudySync</title>
        <style>
            body { font-family: Arial; background:#0f172a; color:white; padding:40px; }
            .card { max-width:420px; background:#111827; padding:28px; border-radius:16px; border:1px solid #243047; }
            label { display:block; margin-top:14px; color:#bfdbfe; }
            input { width:100%; padding:12px; margin-top:6px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white; }
            button { margin-top:20px; width:100%; padding:12px; border:0; border-radius:8px; background:#6366f1; color:white; font-weight:bold; cursor:pointer; }
            a { color:#93c5fd; }
            .message { background:#1e293b; padding:10px; border-radius:8px; margin-bottom:12px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Login to StudySync</h1>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="message">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST">
                <label>Email address</label>
                <input type="email" name="email" value="you@student.uwa.edu.au" required>

                <label>Password</label>
                <input type="password" name="password" value="password123" required>

                <button type="submit">Sign In</button>
            </form>

            <p>Demo login: you@student.uwa.edu.au / password123</p>
            <p><a href="/register">Create account</a> | <a href="/">Back home</a></p>
        </div>
    </body>
    </html>
    """)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        uwa_id = request.form.get("uwa_id", "").strip()
        program = request.form.get("program", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("Full name, email and password are required.")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.")
            return redirect(url_for("auth.register"))

        user = User(full_name=full_name, email=email, uwa_id=uwa_id, program=program, avatar_colour="purple")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. You can now login.")
        return redirect(url_for("auth.login"))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - StudySync</title>
        <style>
            body { font-family: Arial; background:#0f172a; color:white; padding:40px; }
            .card { max-width:480px; background:#111827; padding:28px; border-radius:16px; border:1px solid #243047; }
            label { display:block; margin-top:14px; color:#bfdbfe; }
            input { width:100%; padding:12px; margin-top:6px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white; }
            button { margin-top:20px; width:100%; padding:12px; border:0; border-radius:8px; background:#6366f1; color:white; font-weight:bold; cursor:pointer; }
            a { color:#93c5fd; }
            .message { background:#1e293b; padding:10px; border-radius:8px; margin-bottom:12px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Create StudySync Account</h1>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="message">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <form method="POST">
                <label>Full name</label>
                <input type="text" name="full_name" required>

                <label>Email address</label>
                <input type="email" name="email" required>

                <label>UWA student ID</label>
                <input type="text" name="uwa_id">

                <label>Program</label>
                <input type="text" name="program">

                <label>Password</label>
                <input type="password" name="password" required>

                <label>Confirm password</label>
                <input type="password" name="confirm_password" required>

                <button type="submit">Create Account</button>
            </form>

            <p><a href="/login">Already have an account?</a> | <a href="/">Back home</a></p>
        </div>
    </body>
    </html>
    """)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        return redirect(url_for("auth.login"))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Logout - StudySync</title>
        <style>
            body { font-family: Arial; background:#0f172a; color:white; padding:40px; }
            .card { max-width:420px; background:#111827; padding:28px; border-radius:16px; border:1px solid #243047; }
            button { padding:12px 18px; border:0; border-radius:8px; background:#ef4444; color:white; font-weight:bold; cursor:pointer; }
            a { color:#93c5fd; margin-left:12px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Logout</h1>
            <p>Are you sure you want to logout?</p>
            <form method="POST">
                <button type="submit">Yes, logout</button>
                <a href="/dashboard">Cancel</a>
            </form>
        </div>
    </body>
    </html>
    """)
