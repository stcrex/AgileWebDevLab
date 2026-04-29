from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Course, Exam, Reminder

exams_tasks_bp = Blueprint("exams_tasks", __name__)


def first_available_column(model, options):
    columns = model.__table__.columns.keys()

    for option in options:
        if option in columns:
            return option

    return None


def safe_get(obj, names, default=None):
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


@exams_tasks_bp.route("/exams-tasks")
@login_required
def exams_tasks():
    exam_owner_column = first_available_column(Exam, ["owner_id", "user_id"])
    exam_course_column = first_available_column(Exam, ["course_id", "unit_id"])
    exam_date_column = first_available_column(Exam, ["exam_date", "date", "start_time"])
    exam_title_column = first_available_column(Exam, ["title", "name"])
    exam_location_column = first_available_column(Exam, ["location", "room"])
    exam_weight_column = first_available_column(Exam, ["weight", "weight_percent", "percentage"])

    reminder_owner_column = first_available_column(Reminder, ["owner_id", "user_id"])
    reminder_title_column = first_available_column(Reminder, ["title", "name"])
    reminder_note_column = first_available_column(Reminder, ["note", "description", "message", "body"])
    reminder_time_column = first_available_column(Reminder, ["remind_at", "reminder_time", "due_at", "scheduled_for"])

    exam_query = Exam.query
    if exam_owner_column:
        exam_query = exam_query.filter(getattr(Exam, exam_owner_column) == current_user.id)

    reminder_query = Reminder.query
    if reminder_owner_column:
        reminder_query = reminder_query.filter(getattr(Reminder, reminder_owner_column) == current_user.id)

    exam_rows = exam_query.all()
    reminder_rows = reminder_query.all()

    exams = []
    for exam in exam_rows:
        course_name = "Not linked"
        if exam_course_column:
            course_id = getattr(exam, exam_course_column)
            course = Course.query.get(course_id) if course_id else None
            if course:
                course_name = f"{course.code} - {course.title}"

        exams.append({
            "id": exam.id,
            "title": getattr(exam, exam_title_column) if exam_title_column else "Exam",
            "exam_date": getattr(exam, exam_date_column) if exam_date_column else None,
            "location": getattr(exam, exam_location_column) if exam_location_column else "",
            "weight": getattr(exam, exam_weight_column) if exam_weight_column else None,
            "course_name": course_name,
        })

    exams.sort(key=lambda item: item["exam_date"] or datetime.max)

    reminders = []
    for reminder in reminder_rows:
        reminders.append({
            "id": reminder.id,
            "title": getattr(reminder, reminder_title_column) if reminder_title_column else "Reminder",
            "note": getattr(reminder, reminder_note_column) if reminder_note_column else "",
            "remind_at": getattr(reminder, reminder_time_column) if reminder_time_column else None,
        })

    reminders.sort(key=lambda item: item["remind_at"] or datetime.max)

    return render_template(
        "pages/exams_tasks.html",
        exams=exams,
        reminders=reminders,
    )


@exams_tasks_bp.route("/reminders/new", methods=["GET", "POST"])
@login_required
def create_reminder():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        note = request.form.get("note", "").strip()
        remind_at_text = request.form.get("remind_at", "").strip()

        if not title or not remind_at_text:
            flash("Reminder title and reminder time are required.")
            return render_template("pages/reminder_form.html")

        try:
            remind_at = datetime.fromisoformat(remind_at_text)
        except ValueError:
            flash("Please enter a valid reminder date and time.")
            return render_template("pages/reminder_form.html")

        reminder_data = {}

        title_column = first_available_column(Reminder, ["title", "name"])
        note_column = first_available_column(Reminder, ["note", "description", "message", "body"])
        time_column = first_available_column(Reminder, ["remind_at", "reminder_time", "due_at", "scheduled_for"])
        owner_column = first_available_column(Reminder, ["owner_id", "user_id"])

        if title_column:
            reminder_data[title_column] = title

        if note_column:
            reminder_data[note_column] = note

        if time_column:
            reminder_data[time_column] = remind_at

        if owner_column:
            reminder_data[owner_column] = current_user.id

        reminder = Reminder(**reminder_data)
        db.session.add(reminder)
        db.session.commit()

        flash("Reminder created successfully.")
        return redirect(url_for("exams_tasks.exams_tasks"))

    return render_template("pages/reminder_form.html")


@exams_tasks_bp.route("/reminders/<int:reminder_id>/delete", methods=["POST"])
@login_required
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)

    owner_column = first_available_column(Reminder, ["owner_id", "user_id"])
    if owner_column and getattr(reminder, owner_column) != current_user.id:
        flash("You cannot delete another user's reminder.")
        return redirect(url_for("exams_tasks.exams_tasks"))

    db.session.delete(reminder)
    db.session.commit()

    flash("Reminder deleted successfully.")
    return redirect(url_for("exams_tasks.exams_tasks"))
