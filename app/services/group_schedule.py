"""Merged free slots and booking for study groups (lab slice)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from app.extensions import db
from app.models import CalendarEvent, GroupMember, User


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def week_bounds_mon_fri(monday: date) -> tuple[datetime, datetime]:
    start = datetime.combine(monday, time.min)
    end = datetime.combine(monday + timedelta(days=5), time.min)
    return start, end


def _slot_busy_for_user(user_id: int, slot_start: datetime, slot_end: datetime) -> bool:
    return (
        CalendarEvent.query.filter_by(user_id=user_id)
        .filter(CalendarEvent.start_at < slot_end)
        .filter(CalendarEvent.end_at > slot_start)
        .first()
        is not None
    )


def common_free_slots(group_id: int, monday: date, *, slot_minutes: int = 30) -> list[dict[str, Any]]:
    """Mon–Fri 08:00–20:00 local; slot is free only if no member has a calendar overlap."""
    members = GroupMember.query.filter_by(group_id=group_id).all()
    if not members:
        return []
    user_ids = [m.user_id for m in members]
    n = len(user_ids)
    slot = timedelta(minutes=slot_minutes)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    merged: list[dict[str, Any]] = []

    for wd in range(5):
        d = monday + timedelta(days=wd)
        day_start = datetime.combine(d, time(8, 0))
        day_end = datetime.combine(d, time(20, 0))
        t = day_start
        while t + slot <= day_end:
            slot_end = t + slot
            busy_any = False
            for uid in user_ids:
                if _slot_busy_for_user(uid, t, slot_end):
                    busy_any = True
                    break
            if not busy_any:
                if merged and merged[-1]["end"] == t.isoformat(timespec="minutes"):
                    merged[-1]["end"] = slot_end.isoformat(timespec="minutes")
                else:
                    merged.append(
                        {
                            "day": day_names[wd],
                            "date": d.isoformat(),
                            "start": t.isoformat(timespec="minutes"),
                            "end": slot_end.isoformat(timespec="minutes"),
                            "member_count": n,
                        }
                    )
            t = slot_end

    return merged


def _parse_iso_minutes(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def interval_covered_by_free_slots(
    slots: list[dict[str, Any]], start: datetime, end: datetime
) -> bool:
    """True if [start, end) lies inside the union of merged free intervals (same logic as common_free_slots output)."""
    if start >= end:
        return False
    for s in slots:
        s0 = _parse_iso_minutes(s["start"])
        s1 = _parse_iso_minutes(s["end"])
        if s0 <= start and s1 >= end:
            return True
    return False


def book_free_slot_for_user(
    *,
    user_id: int,
    group_id: int,
    start: datetime,
    end: datetime,
    title: str = "Group study (booked)",
) -> tuple[CalendarEvent | None, str | None]:
    """
    If [start, end) is a subset of a common free slot for the group and the user has no overlap, persist one event.

    Returns (event, None) on success, or (None, error_code) where error_code is
    'not_member' | 'bad_time' | 'not_free' | 'conflict'.
    """
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if member is None:
        return None, "not_member"

    if start >= end:
        return None, "bad_time"

    monday = monday_of(start.date())
    free = common_free_slots(group_id, monday)
    if not interval_covered_by_free_slots(free, start, end):
        return None, "not_free"

    if _slot_busy_for_user(user_id, start, end):
        return None, "conflict"

    ev = CalendarEvent(
        user_id=user_id,
        title=title,
        event_type="group_study",
        start_at=start,
        end_at=end,
        notes=f"Booked from group {group_id}",
    )
    db.session.add(ev)
    db.session.commit()
    return ev, None
