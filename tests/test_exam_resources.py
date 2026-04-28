from __future__ import annotations


def _login(client, email: str = "alice@lab.local"):
    return client.post(
        "/login",
        data={"email": email, "password": "labdemo123"},
        follow_redirects=True,
    )


def test_exam_resources_list_requires_owner(client):
    _login(client, "alice@lab.local")
    rv = client.get("/api/exams/1/resources")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "resources" in data
    assert len(data["resources"]) >= 1


def test_exam_resources_forbidden_for_other_user(client):
    _login(client, "bob@lab.local")
    rv = client.get("/api/exams/1/resources")
    assert rv.status_code == 404


def test_create_resource_validation(client):
    _login(client, "alice@lab.local")
    rv = client.post(
        "/api/exams/1/resources",
        json={"title": "Bad", "url": "ftp://example.com/file"},
        headers={"Content-Type": "application/json"},
    )
    assert rv.status_code == 400
    assert "http" in (rv.get_json() or {}).get("error", "").lower()


def test_create_and_patch_and_delete_resource(client):
    _login(client, "alice@lab.local")
    rv = client.post(
        "/api/exams/1/resources",
        json={"title": "Lecture notes", "url": "https://example.org/notes"},
        headers={"Content-Type": "application/json"},
    )
    assert rv.status_code == 201
    rid = rv.get_json()["resource"]["id"]

    patch = client.patch(
        f"/api/exams/1/resources/{rid}",
        json={"title": "Lecture notes (updated)", "sort_order": 5},
        headers={"Content-Type": "application/json"},
    )
    assert patch.status_code == 200
    assert patch.get_json()["resource"]["title"].startswith("Lecture")
    assert patch.get_json()["resource"]["sort_order"] == 5

    delete = client.delete(f"/api/exams/1/resources/{rid}")
    assert delete.status_code == 204

    again = client.get("/api/exams/1/resources")
    ids = [r["id"] for r in again.get_json()["resources"]]
    assert rid not in ids
