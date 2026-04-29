from __future__ import annotations

from datetime import date, datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import GroupMember, StudyGroup
from app.services.group_schedule import book_free_slot_for_user, common_free_slots, monday_of

bp = Blueprint("group_book", __name__)


def _parse_week_start(raw: str | None):
    if not raw:
        return None
    try:
        from datetime import date

        d = date.fromisoformat(raw)
    except ValueError:
        return None
    return monday_of(d)


def _group_if_member(group_id: int) -> StudyGroup | None:
    g = db.session.get(StudyGroup, group_id)
    if g is None:
        return None
    if GroupMember.query.filter_by(group_id=group_id, user_id=current_user.id).first() is None:
        return None
    return g


@bp.get("/group/<int:group_id>")
@login_required
def group_page(group_id: int):
    if _group_if_member(group_id) is None:
        return render_template("group_book.html", group=None, group_id=group_id), 404
    g = db.session.get(StudyGroup, group_id)
    week_start_iso = monday_of(date.today()).isoformat()
    return render_template(
        "group_book.html", group=g, group_id=group_id, week_start_iso=week_start_iso
    )


@bp.get("/api/groups/<int:group_id>/free-slots")
@login_required
def api_free_slots(group_id: int):
    if _group_if_member(group_id) is None:
        return jsonify({"error": "Not found."}), 404
    ws = _parse_week_start(request.args.get("week_start"))
    if ws is None:
        return jsonify({"error": "Invalid or missing week_start (YYYY-MM-DD)."}), 400
    slots = common_free_slots(group_id, ws)
    return jsonify({"week_start": ws.isoformat(), "slots": slots})


@bp.post("/api/groups/<int:group_id>/book-free-slot")
@login_required
def api_book_free_slot(group_id: int):
    if _group_if_member(group_id) is None:
        return jsonify({"error": "Not found."}), 404
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400
    data = request.get_json(silent=True) or {}
    start_raw = data.get("start")
    end_raw = data.get("end")
    if not start_raw or not end_raw:
        return jsonify({"error": "start and end ISO datetimes are required."}), 400
    try:
        start = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "Invalid start or end datetime."}), 400

    ev, err = book_free_slot_for_user(user_id=current_user.id, group_id=group_id, start=start, end=end)
    if err == "not_member":
        return jsonify({"error": "Not found."}), 404
    if err == "bad_time":
        return jsonify({"error": "end must be after start."}), 400
    if err == "not_free":
        return jsonify({"error": "That interval is not inside a common free slot for this week."}), 409
    if err == "conflict":
        return jsonify({"error": "You already have an event overlapping that time."}), 409
    assert ev is not None
    return jsonify({"event": ev.to_dict()}), 201
