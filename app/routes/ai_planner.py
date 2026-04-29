from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models import Exam, Reminder, TimetableEvent

ai_planner_bp = Blueprint("ai_planner", __name__)


def first_available_column(model, options):
    """
    Return the first matching column name that exists on the model.
    This keeps the route flexible even if model column names vary slightly.
    """
    columns = model.__table__.columns.keys()

    for option in options:
        if option in columns:
            return option

    return None


def get_user_events():
    """
    Get timetable events for the current user, ordered by start time.
    """
    query = TimetableEvent.query

    if "owner_id" in TimetableEvent.__table__.columns.keys():
        query = query.filter(TimetableEvent.owner_id == current_user.id)

    return query.order_by(TimetableEvent.start_time.asc()).all()


def get_user_exams():
    """
    Get exams for the current user, ordered by exam date if available.
    """
    exam_owner_column = first_available_column(Exam, ["owner_id", "user_id"])
    exam_date_column = first_available_column(Exam, ["exam_date", "date", "start_time"])

    query = Exam.query

    if exam_owner_column:
        query = query.filter(getattr(Exam, exam_owner_column) == current_user.id)

    exams = query.all()

    if exam_date_column:
        exams.sort(key=lambda exam: getattr(exam, exam_date_column) or datetime.max)

    return exams


def get_user_reminders():
    """
    Get reminders for the current user, ordered by reminder time if available.
    """
    reminder_owner_column = first_available_column(Reminder, ["owner_id", "user_id"])
    reminder_time_column = first_available_column(Reminder, ["remind_at", "reminder_time", "due_at", "scheduled_for"])

    query = Reminder.query

    if reminder_owner_column:
        query = query.filter(getattr(Reminder, reminder_owner_column) == current_user.id)

    reminders = query.all()

    if reminder_time_column:
        reminders.sort(key=lambda reminder: getattr(reminder, reminder_time_column) or datetime.max)

    return reminders


def format_dt(value):
    """
    Format a datetime nicely for display.
    """
    if not value:
        return "Not scheduled"
    return value.strftime("%a %d %b, %I:%M %p")


def exam_title(exam):
    title_column = first_available_column(Exam, ["title", "name"])
    return getattr(exam, title_column) if title_column else "Exam"


def exam_date(exam):
    date_column = first_available_column(Exam, ["exam_date", "date", "start_time"])
    return getattr(exam, date_column) if date_column else None


def reminder_title(reminder):
    title_column = first_available_column(Reminder, ["title", "name"])
    return getattr(reminder, title_column) if title_column else "Reminder"


def reminder_note(reminder):
    note_column = first_available_column(Reminder, ["note", "description", "message", "body"])
    return getattr(reminder, note_column) if note_column else ""


def reminder_time(reminder):
    time_column = first_available_column(Reminder, ["remind_at", "reminder_time", "due_at", "scheduled_for"])
    return getattr(reminder, time_column) if time_column else None


def build_ai_reply(prompt, events, exams, reminders):
    """
    Generate a smart response using local database data.
    No external API is needed.
    """
    now = datetime.now()
    prompt_lower = prompt.lower()

    week_end = now + timedelta(days=7)

    upcoming_events = [event for event in events if event.start_time >= now]
    week_events = [event for event in events if now <= event.start_time <= week_end]
    upcoming_exams = [exam for exam in exams if exam_date(exam) and exam_date(exam) >= now]
    upcoming_reminders = [reminder for reminder in reminders if reminder_time(reminder) and reminder_time(reminder) >= now]

    response = {
        "heading": "StudySync AI Plan",
        "summary": "",
        "bullets": [],
    }

    if "today" in prompt_lower:
        today_events = [event for event in events if event.start_time.date() == now.date()]

        response["heading"] = "Today's Study Plan"

        if today_events:
            response["summary"] = "Here is your schedule for today."
            for event in today_events:
                response["bullets"].append(
                    f"{event.title} ({event.event_type}) at {format_dt(event.start_time)}"
                )
        else:
            response["summary"] = "You do not have any timetable events today."
            response["bullets"].append("Use today for revision, assignments, or project work.")

        if upcoming_exams:
            response["bullets"].append(
                f"Nearest exam: {exam_title(upcoming_exams[0])} on {format_dt(exam_date(upcoming_exams[0]))}."
            )

    elif "week" in prompt_lower or "timetable" in prompt_lower:
        response["heading"] = "This Week's Timetable Plan"

        if week_events:
            response["summary"] = "These are your upcoming events for the next 7 days."
            for event in week_events[:6]:
                response["bullets"].append(
                    f"{event.title} ({event.event_type}) on {format_dt(event.start_time)}"
                )
        else:
            response["summary"] = "You do not have any upcoming timetable events this week."
            response["bullets"].append("Plan self-study blocks for your weakest subjects.")

        if upcoming_exams:
            response["bullets"].append(
                f"Also prepare for {exam_title(upcoming_exams[0])}, your next exam."
            )

    elif "exam" in prompt_lower or "study" in prompt_lower or "prepare" in prompt_lower:
        response["heading"] = "Exam Preparation Plan"

        if upcoming_exams:
            next_exam = upcoming_exams[0]
            response["summary"] = f"Your nearest exam is {exam_title(next_exam)} on {format_dt(exam_date(next_exam))}."
            response["bullets"].append("Revise lecture summaries first, then attempt practice questions.")
            response["bullets"].append("Use free timetable gaps for focused revision blocks.")
            response["bullets"].append("Finish one full exam-style revision session before the exam date.")
            if week_events:
                response["bullets"].append(
                    f"You still have {len(week_events)} timetable event(s) this week, so plan around them."
                )
        else:
            response["summary"] = "You do not have any upcoming exams saved right now."
            response["bullets"].append("Add exams from the Courses page so I can build better study plans.")

    elif "reminder" in prompt_lower or "task" in prompt_lower or "due" in prompt_lower:
        response["heading"] = "Tasks and Reminders Overview"

        if upcoming_reminders:
            response["summary"] = "These are your next reminders."
            for reminder in upcoming_reminders[:5]:
                extra_note = reminder_note(reminder)
                line = f"{reminder_title(reminder)} at {format_dt(reminder_time(reminder))}"
                if extra_note:
                    line += f" — {extra_note}"
                response["bullets"].append(line)
        else:
            response["summary"] = "You do not have upcoming reminders saved yet."
            response["bullets"].append("Add reminders for assignments, exams, and project deadlines.")

    else:
        response["heading"] = "Smart Weekly Overview"
        response["summary"] = "Here is a quick summary of your current study situation."

        if upcoming_exams:
            response["bullets"].append(
                f"Next exam: {exam_title(upcoming_exams[0])} on {format_dt(exam_date(upcoming_exams[0]))}."
            )
        else:
            response["bullets"].append("No upcoming exams are currently saved.")

        if week_events:
            response["bullets"].append(f"You have {len(week_events)} timetable event(s) in the next 7 days).")
        else:
            response["bullets"].append("No timetable events are scheduled in the next 7 days.")

        if upcoming_reminders:
            response["bullets"].append(f"You have {len(upcoming_reminders)} active reminder(s) coming up.")
        else:
            response["bullets"].append("No upcoming reminders are currently saved.")

        response["bullets"].append("Focus first on the nearest deadline or exam.")
        response["bullets"].append("Use shorter revision blocks between lectures and longer blocks on free days.")

    return response


@ai_planner_bp.route("/ai-planner", methods=["GET", "POST"])
@login_required
def ai_planner():
    events = get_user_events()
    exams = get_user_exams()
    reminders = get_user_reminders()

    response = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()

        if not prompt:
            flash("Please enter a question or choose a quick prompt.")
        else:
            response = build_ai_reply(prompt, events, exams, reminders)

            history = session.get("ai_planner_history", [])
            history.append({
                "prompt": prompt,
                "heading": response["heading"],
                "summary": response["summary"],
                "created_at": datetime.now().strftime("%d %b, %I:%M %p"),
            })
            session["ai_planner_history"] = history[-6:]

    history = session.get("ai_planner_history", [])

    upcoming_exam = None
    for exam in exams:
        when = exam_date(exam)
        if when and when >= datetime.now():
            upcoming_exam = exam
            break

    return render_template(
        "pages/ai_planner.html",
        response=response,
        history=list(reversed(history)),
        upcoming_exam=upcoming_exam,
        upcoming_exam_title=exam_title(upcoming_exam) if upcoming_exam else None,
        upcoming_exam_date=format_dt(exam_date(upcoming_exam)) if upcoming_exam else "No upcoming exam",
        week_event_count=len([event for event in events if datetime.now() <= event.start_time <= datetime.now() + timedelta(days=7)]),
        reminder_count=len([rem for rem in reminders if reminder_time(rem) and reminder_time(rem) >= datetime.now()]),
    )


@ai_planner_bp.route("/ai-planner/clear-history", methods=["POST"])
@login_required
def clear_history():
    session["ai_planner_history"] = []
    flash("AI planner history cleared.")
    return redirect(url_for("ai_planner.ai_planner"))

