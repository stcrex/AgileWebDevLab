"""Per-user reminders: list, create, toggle done, delete."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import nullslast

from app.extensions import db
from app.models import Reminder

bp = Blueprint("reminders", __name__)

MAX_TITLE = 160


def _parse_due_at(raw: str | None) -> datetime | None:
    """Parse HTML datetime-local (naive local time) into a naive datetime."""
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip()
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _reminder_owned(reminder_id: int) -> Reminder | None:
    r = db.session.get(Reminder, reminder_id)
    if r is None or r.owner_id != current_user.id:
        return None
    return r


@bp.get("/reminders")
@login_required
def reminders_list():
    rows = (
        Reminder.query.filter_by(owner_id=current_user.id)
        .order_by(Reminder.is_done.asc(), nullslast(Reminder.due_at.asc()), Reminder.id.asc())
        .all()
    )
    return render_template("reminders.html", reminders=rows)


@bp.post("/reminders")
@login_required
def reminders_create():
    title = (request.form.get("title") or "").strip()
    due_raw = request.form.get("due_at")
    if not title:
        flash("Title is required.", "warning")
        return redirect(url_for("reminders.reminders_list"))
    if len(title) > MAX_TITLE:
        flash("Title is too long.", "warning")
        return redirect(url_for("reminders.reminders_list"))
    due_at = _parse_due_at(due_raw)
    if due_raw and due_raw.strip() and due_at is None:
        flash("Due date could not be parsed; reminder saved without a due time.", "info")
    r = Reminder(title=title, due_at=due_at, is_done=False, owner_id=current_user.id)
    db.session.add(r)
    db.session.commit()
    flash("Reminder added.", "success")
    return redirect(url_for("reminders.reminders_list"))


@bp.post("/reminders/<int:reminder_id>/toggle")
@login_required
def reminders_toggle(reminder_id: int):
    r = _reminder_owned(reminder_id)
    if r is None:
        flash("Reminder not found.", "danger")
        return redirect(url_for("reminders.reminders_list"))
    r.is_done = not bool(r.is_done)
    db.session.commit()
    return redirect(url_for("reminders.reminders_list"))


@bp.post("/reminders/<int:reminder_id>/delete")
@login_required
def reminders_delete(reminder_id: int):
    r = _reminder_owned(reminder_id)
    if r is None:
        flash("Reminder not found.", "danger")
        return redirect(url_for("reminders.reminders_list"))
    db.session.delete(r)
    db.session.commit()
    flash("Reminder removed.", "info")
    return redirect(url_for("reminders.reminders_list"))
