from flask import Blueprint, render_template_string

from app.models import Course, Exam, GroupMessage, StudyGroup, TimetableEvent, User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudySync</title>
        </head>
        <body style="font-family: Arial; background:#0f172a; color:white; padding:40px;">
            <h1>StudySync Flask App Running</h1>
            <p>The Flask backend setup is working.</p>
            <p>Stage 2 adds database models and demo seed data.</p>
            <p><a href="/db-check" style="color:#93c5fd;">Check database demo data</a></p>
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
        """
        ,
        user_count=user_count,
        course_count=course_count,
        event_count=event_count,
        exam_count=exam_count,
        group_count=group_count,
        message_count=message_count
    )
