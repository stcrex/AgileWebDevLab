"""Sidebar-linked pages (courses, reminders, preferences)."""

from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Course, ExamSession

bp = Blueprint("sidebar_stubs", __name__)


def _rollup_course_codes_from_exams(user_id: int) -> list[dict]:
    """One row per distinct course_code on the user's exam sessions (chronological tie-break)."""
    rows = (
        ExamSession.query.filter_by(user_id=user_id)
        .order_by(ExamSession.starts_at.asc())
        .all()
    )
    by_code: dict[str, list[ExamSession]] = defaultdict(list)
    for ex in rows:
        label = (ex.course_code or "").strip() or "—"
        by_code[label].append(ex)
    out: list[dict] = []
    for code in sorted(by_code.keys(), key=lambda c: (c == "—", c.lower())):
        ordered = sorted(by_code[code], key=lambda s: s.starts_at)
        nxt = ordered[0]
        out.append(
            {
                "code": code,
                "exam_count": len(ordered),
                "next_starts": nxt.starts_at,
                "next_exam_id": nxt.id,
            }
        )
    return out


@bp.get("/courses")
@login_required
def courses_stub():
    catalog = Course.query.filter_by(owner_id=current_user.id).order_by(Course.code.asc()).all()
    from_exams = _rollup_course_codes_from_exams(current_user.id)
    return render_template(
        "courses.html",
        catalog_courses=catalog,
        from_exams=from_exams,
    )


@bp.get("/reminders")
@login_required
def reminders_stub():
    return render_template("reminders_stub.html")


@bp.get("/preferences")
@login_required
def preferences_stub():
    return render_template("preferences_stub.html")
