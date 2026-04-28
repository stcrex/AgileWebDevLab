from datetime import date, datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Course, TimetableEvent

timetable_bp = Blueprint("timetable", __name__)


def get_week_start():
    start_value = request.args.get("start")

    if start_value:
        try:
            return datetime.strptime(start_value, "%Y-%m-%d").date()
        except ValueError:
            pass

    return date(2026, 4, 13)


@timetable_bp.route("/timetable")
@login_required
def timetable():
    week_start = get_week_start()
    week_end = week_start + timedelta(days=7)

    events = (
        TimetableEvent.query
        .filter(TimetableEvent.owner_id == current_user.id)
        .filter(TimetableEvent.start_time >= datetime.combine(week_start, datetime.min.time()))
        .filter(TimetableEvent.start_time < datetime.combine(week_end, datetime.min.time()))
        .order_by(TimetableEvent.start_time.asc())
        .all()
    )

    days = []

    for index in range(5):
        current_day = week_start + timedelta(days=index)
        day_events = [
            event for event in events
            if event.start_time.date() == current_day
        ]

        days.append({
            "date": current_day,
            "label": current_day.strftime("%A"),
            "events": day_events,
        })

    return render_template(
        "pages/timetable.html",
        week_start=week_start,
        week_end=week_end - timedelta(days=1),
        previous_week=week_start - timedelta(days=7),
        next_week=week_start + timedelta(days=7),
        days=days,
    )


@timetable_bp.route("/timetable/events/new", methods=["GET", "POST"])
@login_required
def create_event():
    courses = Course.query.filter_by(owner_id=current_user.id).order_by(Course.code.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        event_type = request.form.get("event_type", "").strip()
        location = request.form.get("location", "").strip()
        start_time_text = request.form.get("start_time", "")
        end_time_text = request.form.get("end_time", "")
        course_id_text = request.form.get("course_id", "")

        if not title or not event_type or not start_time_text or not end_time_text:
            flash("Title, type, start time and end time are required.")
            return render_template("pages/event_form.html", courses=courses)

        try:
            start_time = datetime.fromisoformat(start_time_text)
            end_time = datetime.fromisoformat(end_time_text)
        except ValueError:
            flash("Please enter valid start and end times.")
            return render_template("pages/event_form.html", courses=courses)

        if end_time <= start_time:
            flash("End time must be after start time.")
            return render_template("pages/event_form.html", courses=courses)

        course_id = None
        if course_id_text:
            course = Course.query.filter_by(id=int(course_id_text), owner_id=current_user.id).first()
            if course:
                course_id = course.id

        event = TimetableEvent(
            title=title,
            event_type=event_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            owner_id=current_user.id,
            course_id=course_id,
            is_group_event=False,
        )

        db.session.add(event)
        db.session.commit()

        flash("Event created successfully.")
        return redirect(url_for("timetable.timetable", start=start_time.date().isoformat()))

    return render_template("pages/event_form.html", courses=courses)


@timetable_bp.route("/timetable/events/<int:event_id>")
@login_required
def event_detail(event_id):
    event = TimetableEvent.query.filter_by(
        id=event_id,
        owner_id=current_user.id
    ).first_or_404()

    return render_template("pages/event_detail.html", event=event)


@timetable_bp.route("/timetable/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    event = TimetableEvent.query.filter_by(
        id=event_id,
        owner_id=current_user.id
    ).first_or_404()

    event_date = event.start_time.date()

    db.session.delete(event)
    db.session.commit()

    flash("Event deleted successfully.")
    return redirect(url_for("timetable.timetable", start=event_date.isoformat()))
