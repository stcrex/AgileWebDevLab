from __future__ import annotations

from datetime import date, datetime, time, timedelta

from app.models import GroupMember, GroupMessage, User


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


def test_group_workspace_requires_login(client):
    rv = client.get("/group/1", follow_redirects=False)
    assert rv.status_code in (302, 401)


def test_group_workspace_renders_for_member(client):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    rv = client.get("/group/1")
    assert rv.status_code == 200
    body = rv.data.decode()
    assert "Messages" in body
    assert "Members" in body
    assert "Common free slots" in body


def test_group_chat_redirect_sends_member_to_workspace(client):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    rv = client.get("/group-chat", follow_redirects=False)
    assert rv.status_code == 302
    assert "/group/1" in (rv.headers.get("Location") or "")


def test_post_group_message_persists(client, app):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    with app.app_context():
        n0 = GroupMessage.query.filter_by(group_id=1).count()
    rv = client.post("/group/1/message", data={"message": "hello workspace"})
    assert rv.status_code == 302
    with app.app_context():
        assert GroupMessage.query.filter_by(group_id=1).count() == n0 + 1
        last = (
            GroupMessage.query.filter_by(group_id=1).order_by(GroupMessage.id.desc()).first()
        )
        assert last is not None
        assert last.body == "hello workspace"


def test_post_group_message_for_unknown_group_is_404(client):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    rv = client.post("/group/99999/message", data={"message": "nope"})
    assert rv.status_code == 404


def test_invite_adds_member_and_user(client, app):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    email = "carol.invite@lab.local"
    rv = client.post(
        "/group/1/invite",
        data={"email": email, "full_name": "Carol Invite"},
    )
    assert rv.status_code == 302
    with app.app_context():
        u = User.query.filter_by(email=email).first()
        assert u is not None
        assert u.full_name == "Carol Invite"
        assert GroupMember.query.filter_by(group_id=1, user_id=u.id).first() is not None


def test_invite_existing_member_does_not_duplicate_row(client, app):
    client.post(
        "/login",
        data={"email": "alice@lab.local", "password": "labdemo123"},
        follow_redirects=True,
    )
    with app.app_context():
        n0 = GroupMember.query.filter_by(group_id=1).count()
        m0 = GroupMessage.query.filter_by(group_id=1).count()
    rv = client.post(
        "/group/1/invite",
        data={"email": "bob@lab.local", "full_name": "Bob Lab"},
    )
    assert rv.status_code == 302
    with app.app_context():
        assert GroupMember.query.filter_by(group_id=1).count() == n0
        assert GroupMessage.query.filter_by(group_id=1).count() == m0
