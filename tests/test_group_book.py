from __future__ import annotations

from datetime import date, datetime, time, timedelta


def _monday():
    d = date.today()
    return d - timedelta(days=d.weekday())


def test_api_free_slots_requires_auth(client):
    ws = _monday().isoformat()
    rv = client.get(f"/api/groups/1/free-slots?week_start={ws}")
    assert rv.status_code == 401


def test_book_flow_happy_path_then_conflict(client):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    ws = _monday().isoformat()
    rv = client.get(f"/api/groups/1/free-slots?week_start={ws}")
    assert rv.status_code == 200
    payload = rv.get_json()
    assert "slots" in payload
    slots = payload["slots"]
    assert isinstance(slots, list)
    assert len(slots) >= 1
    slot = slots[0]
    book = client.post(
        "/api/groups/1/book-free-slot",
        json={"start": slot["start"], "end": slot["end"]},
        headers={"Content-Type": "application/json"},
    )
    assert book.status_code == 201
    ev = book.get_json()["event"]
    assert ev["event_type"] == "group_study"

    again = client.post(
        "/api/groups/1/book-free-slot",
        json={"start": slot["start"], "end": slot["end"]},
        headers={"Content-Type": "application/json"},
    )
    assert again.status_code == 409


def test_book_rejects_interval_outside_common_free_grid(client):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    monday = _monday()
    # Interval clearly outside Mon–Fri 08:00–20:00 free grid
    start = datetime.combine(monday, time(6, 0))
    end = datetime.combine(monday, time(6, 30))
    rv = client.post(
        "/api/groups/1/book-free-slot",
        json={"start": start.isoformat(timespec="minutes"), "end": end.isoformat(timespec="minutes")},
        headers={"Content-Type": "application/json"},
    )
    assert rv.status_code == 409
    assert "not inside" in (rv.get_json() or {}).get("error", "").lower()
