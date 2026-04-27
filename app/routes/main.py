from flask import Blueprint, render_template_string
from flask_login import current_user, login_required

from app.models import Course, Exam, GroupMessage, StudyGroup, TimetableEvent, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>StudySync</title>
            </head>
            <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
                <h1>Welcome back, {{ current_user.full_name }}</h1>
                <p>You are logged in to StudySync.</p>
                <p><a href="/dashboard" style="color:#93c5fd;">Open Dashboard</a></p>
                <p><a href="/logout" style="color:#fca5a5;">Logout</a></p>
            </body>
            </html>
            """
        )

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudySync</title>
        </head>
        <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
            <h1>StudySync Flask App Running</h1>
            <p>The Flask backend, database and authentication setup are working.</p>
            <p>
                <a href="/login" style="color:#93c5fd;">Login</a>
                |
                <a href="/register" style="color:#93c5fd;">Register</a>
                |
                <a href="/db-check" style="color:#93c5fd;">Check Database</a>
            </p>
        </body>
        </html>
        """
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudySync Dashboard</title>
        </head>
        <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
            <h1>Dashboard</h1>
            <p>Hello, {{ current_user.full_name }}.</p>
            <p>Email: {{ current_user.email }}</p>
            <p>Program: {{ current_user.program or "Not added yet" }}</p>
            <p>This page proves login sessions are working.</p>
            <p>
                <a href="/db-check" style="color:#93c5fd;">Database Check</a>
                |
                <a href="/logout" style="color:#fca5a5;">Logout</a>
            </p>
        </body>
        </html>
        """
    )


@main_bp.route("/db-check")
def db_check():
    user_count = User.query.count()
    course_count = Course.query.count()
    event_count = TimetableEvent.query.count()
    exam_count = Exam.query.count()
    group_count = StudyGroup.query.count()
    message_count = GroupMessage.query.count()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudySync Database Check</title>
        </head>
        <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
            <h1>Database Check</h1>
            <p>If these numbers are above 0, the database seed worked.</p>
            <ul>
                <li>Users: {{ user_count }}</li>
                <li>Courses: {{ course_count }}</li>
                <li>Timetable events: {{ event_count }}</li>
                <li>Exams: {{ exam_count }}</li>
                <li>Study groups: {{ group_count }}</li>
                <li>Group messages: {{ message_count }}</li>
            </ul>
            <p><a href="/" style="color:#93c5fd;">Back to home</a></p>
        </body>
        </html>
        """,
        user_count=user_count,
        course_count=course_count,
        event_count=event_count,
        exam_count=exam_count,
        group_count=group_count,
        message_count=message_count,
    )
