from __future__ import annotations


def _login(client, email: str = "alice@lab.local"):
    return client.post("/login", data={"email": email, "password": "labdemo123"}, follow_redirects=True)


def test_preferences_requires_login(client):
    rv = client.get("/preferences", follow_redirects=False)
    assert rv.status_code in (302, 303)


def test_preferences_get_ok(client):
    _login(client, "alice@lab.local")
    rv = client.get("/preferences")
    assert rv.status_code == 200
    assert b"alice@lab.local" in rv.data
    assert b"Save preferences" in rv.data
    assert b"Profile completeness" in rv.data


def test_preferences_uwa_id_invalid(client):
    _login(client, "alice@lab.local")
    rv = client.post(
        "/preferences",
        data={
            "full_name": "Alice Lab",
            "uwa_id": "12345",
            "program": "",
            "bio": "",
            "skills": "",
            "availability": "",
            "avatar_colour": "purple",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"UWA ID" in rv.data


def test_preferences_update_profile(client, app):
    _login(client, "alice@lab.local")
    rv = client.post(
        "/preferences",
        data={
            "full_name": "Alice Updated",
            "uwa_id": "12345678",
            "program": "MIT",
            "bio": "Hello lab",
            "skills": "Flask",
            "availability": "Weekdays",
            "avatar_colour": "blue",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Preferences saved" in rv.data
    with app.app_context():
        from app.models import User

        u = User.query.filter_by(email="alice@lab.local").first()
        assert u.full_name == "Alice Updated"
        assert u.uwa_id == "12345678"
        assert u.program == "MIT"
        assert u.bio == "Hello lab"
        assert u.skills == "Flask"
        assert u.availability == "Weekdays"
        assert u.avatar_colour == "blue"


def test_preferences_empty_name_rejected(client):
    _login(client, "bob@lab.local")
    rv = client.post(
        "/preferences",
        data={
            "full_name": "  ",
            "uwa_id": "",
            "program": "",
            "bio": "",
            "skills": "",
            "availability": "",
            "avatar_colour": "green",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"Full name is required" in rv.data


def test_preferences_invalid_colour_ignored(client, app):
    _login(client, "bob@lab.local")
    with app.app_context():
        from app.extensions import db
        from app.models import User

        u = User.query.filter_by(email="bob@lab.local").first()
        u.avatar_colour = "orange"
        db.session.commit()

    client.post(
        "/preferences",
        data={
            "full_name": "Bob Lab",
            "uwa_id": "",
            "program": "",
            "bio": "",
            "skills": "",
            "availability": "",
            "avatar_colour": "not-a-real-colour",
        },
        follow_redirects=True,
    )
    with app.app_context():
        from app.models import User

        u = User.query.filter_by(email="bob@lab.local").first()
        assert u.avatar_colour == "orange"
