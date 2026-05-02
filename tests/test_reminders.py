from __future__ import annotations


def _login(client, email: str = "alice@lab.local"):
    return client.post("/login", data={"email": email, "password": "labdemo123"}, follow_redirects=True)


def test_reminders_requires_login(client):
    rv = client.get("/reminders", follow_redirects=False)
    assert rv.status_code in (302, 303)


def test_reminders_list_ok_for_alice(client):
    _login(client, "alice@lab.local")
    rv = client.get("/reminders")
    assert rv.status_code == 200
    assert b"Reminders" in rv.data


def test_reminders_create_toggle_delete_flow(client):
    _login(client, "alice@lab.local")
    rv = client.post(
        "/reminders",
        data={"title": "Unit test reminder", "due_at": ""},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Unit test reminder" in rv.data

    from app.extensions import db
    from app.models import Reminder, User

    with client.application.app_context():
        u = User.query.filter_by(email="alice@lab.local").first()
        r = Reminder.query.filter_by(owner_id=u.id, title="Unit test reminder").first()
        assert r is not None
        rid = r.id
        assert r.is_done is False

    client.post(f"/reminders/{rid}/toggle", follow_redirects=True)
    with client.application.app_context():
        r2 = db.session.get(Reminder, rid)
        assert r2 is not None and r2.is_done is True

    client.post(f"/reminders/{rid}/delete", follow_redirects=True)
    with client.application.app_context():
        assert db.session.get(Reminder, rid) is None


def test_reminders_bob_cannot_toggle_alice_reminder(client, app):
    with app.app_context():
        from app.extensions import db
        from app.models import Reminder, User

        alice = User.query.filter_by(email="alice@lab.local").first()
        r = Reminder(title="Alice only", owner_id=alice.id, is_done=False)
        db.session.add(r)
        db.session.commit()
        rid = r.id

    _login(client, "bob@lab.local")
    client.post(f"/reminders/{rid}/toggle", follow_redirects=True)
    with app.app_context():
        r2 = db.session.get(Reminder, rid)
        assert r2 is not None and r2.is_done is False


def test_reminders_empty_title_rejected(client):
    _login(client, "alice@lab.local")
    rv = client.post("/reminders", data={"title": "  ", "due_at": ""}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Title is required" in rv.data
