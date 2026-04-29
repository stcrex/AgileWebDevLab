from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Course, Exam, TimetableEvent

courses_bp = Blueprint("courses", __name__)


def first_available_column(model, options):
    """
    Helper function.

    Some model files may use slightly different column names.
    This checks which column name exists before we use it.
    """
    columns = model.__table__.columns.keys()

    for option in options:
        if option in columns:
            return option

    return None


def create_exam_for_course(course, title, start_time, location, weight):
    """
    Create an exam while supporting different possible Exam model column names.
    This keeps the route beginner-friendly and avoids column-name errors.
    """
    exam_data = {}

    title_column = first_available_column(Exam, ["title", "name"])
    course_column = first_available_column(Exam, ["course_id", "unit_id"])
    owner_column = first_available_column(Exam, ["owner_id", "user_id"])
    date_column = first_available_column(Exam, ["exam_date", "date", "start_time"])
    location_column = first_available_column(Exam, ["location", "room"])
    weight_column = first_available_column(Exam, ["weight", "weight_percent", "percentage"])

    if title_column:
        exam_data[title_column] = title

    if course_column:
        exam_data[course_column] = course.id

    if owner_column:
        exam_data[owner_column] = current_user.id

    if date_column:
        exam_data[date_column] = start_time

    if location_column:
        exam_data[location_column] = location

    if weight_column:
        exam_data[weight_column] = weight

    exam = Exam(**exam_data)
    db.session.add(exam)
    db.session.commit()


@courses_bp.route("/courses")
@login_required
def courses():
    """
    Show all courses belonging to the logged-in student.
    """
    course_list = (
        Course.query
        .filter_by(owner_id=current_user.id)
        .order_by(Course.code.asc())
        .all()
    )

    course_cards = []

    for course in course_list:
        event_count = TimetableEvent.query.filter_by(
            owner_id=current_user.id,
            course_id=course.id
        ).count()

        exam_count = Exam.query.filter_by(
            owner_id=current_user.id,
            course_id=course.id
        ).count()

        course_cards.append({
            "course": course,
            "event_count": event_count,
            "exam_count": exam_count,
        })

    return render_template("pages/courses.html", course_cards=course_cards)


@courses_bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    """
    Show one course with its linked timetable events and exams.
    """
    course = Course.query.filter_by(
        id=course_id,
        owner_id=current_user.id
    ).first_or_404()

    events = (
        TimetableEvent.query
        .filter_by(owner_id=current_user.id, course_id=course.id)
        .order_by(TimetableEvent.start_time.asc())
        .all()
    )

    exams = (
        Exam.query
        .filter_by(owner_id=current_user.id, course_id=course.id)
        .all()
    )

    return render_template(
        "pages/course_detail.html",
        course=course,
        events=events,
        exams=exams,
    )


@courses_bp.route("/courses/<int:course_id>/event", methods=["GET", "POST"])
@login_required
def add_course_event(course_id):
    """
    Add a timetable event already linked to this course.
    """
    course = Course.query.filter_by(
        id=course_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        event_type = request.form.get("event_type", "").strip()
        location = request.form.get("location", "").strip()
        start_time_text = request.form.get("start_time", "")
        end_time_text = request.form.get("end_time", "")

        if not title or not event_type or not start_time_text or not end_time_text:
            flash("Title, type, start time and end time are required.")
            return render_template("pages/course_event_form.html", course=course)

        try:
            start_time = datetime.fromisoformat(start_time_text)
            end_time = datetime.fromisoformat(end_time_text)
        except ValueError:
            flash("Please enter valid date and time values.")
            return render_template("pages/course_event_form.html", course=course)

        if end_time <= start_time:
            flash("End time must be after start time.")
            return render_template("pages/course_event_form.html", course=course)

        event = TimetableEvent(
            title=title,
            event_type=event_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            owner_id=current_user.id,
            course_id=course.id,
            is_group_event=False,
        )

        db.session.add(event)
        db.session.commit()

        flash("Course event created successfully.")
        return redirect(url_for("courses.course_detail", course_id=course.id))

    return render_template("pages/course_event_form.html", course=course)


@courses_bp.route("/courses/<int:course_id>/exam", methods=["GET", "POST"])
@login_required
def add_course_exam(course_id):
    """
    Add an exam already linked to this course.
    """
    course = Course.query.filter_by(
        id=course_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        exam_time_text = request.form.get("exam_time", "")
        weight_text = request.form.get("weight", "0").strip()

        if not title or not exam_time_text:
            flash("Exam title and exam time are required.")
            return render_template("pages/course_exam_form.html", course=course)

        try:
            exam_time = datetime.fromisoformat(exam_time_text)
        except ValueError:
            flash("Please enter a valid exam date and time.")
            return render_template("pages/course_exam_form.html", course=course)

        try:
            weight = float(weight_text)
        except ValueError:
            weight = 0

        create_exam_for_course(course, title, exam_time, location, weight)

        flash("Course exam created successfully.")
        return redirect(url_for("courses.course_detail", course_id=course.id))

    return render_template("pages/course_exam_form.html", course=course)
