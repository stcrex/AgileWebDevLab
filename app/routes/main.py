from flask import Blueprint, render_template, render_template_string
from flask_login import login_required

from app.models import Course, Exam, GroupMessage, StudyGroup, TimetableEvent, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/bootstrap")
def bootstrap_status():
    """Stage-1 style sanity page; kept under /bootstrap so / stays the real app entry."""
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <title>StudySync — bootstrap</title>
        </head>
        <body style="font-family: system-ui, sans-serif; background:#0f172a; color:#f8fafc; padding:40px;">
            <h1>Flask backend reachable</h1>
            <p>Use <a href="/" style="color:#93c5fd;">/</a> for the full lab app.</p>
        </body>
        </html>
        """
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_count = User.query.count()
    course_count = Course.query.count()
    event_count = TimetableEvent.query.count()
    exam_count = Exam.query.count()
    group_count = StudyGroup.query.count()
    message_count = GroupMessage.query.count()

    return render_template(
        "pages/dashboard.html",
        user_count=user_count,
        course_count=course_count,
        event_count=event_count,
        exam_count=exam_count,
        group_count=group_count,
        message_count=message_count,
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