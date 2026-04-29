from __future__ import annotations


def _login(client, email: str = "alice@lab.local"):
    return client.post(
        "/login",
        data={"email": email, "password": "labdemo123"},
        follow_redirects=True,
    )


def test_share_token_requires_auth(client):
    rv = client.post("/api/exams/1/share-token")
    assert rv.status_code == 401


def test_share_public_flow_generate_view_revoke(client):
    _login(client, "alice@lab.local")
    gen = client.post("/api/exams/1/share-token")
    assert gen.status_code == 201
    data = gen.get_json()
    assert "share_token" in data and "share_url" in data
    token = data["share_token"]
    assert len(token) >= 32

    pub = client.get(f"/exams/shared/{token}")
    assert pub.status_code == 200
    assert b"Read-only" in pub.data
    assert b"Practice exam" in pub.data

    bad = client.get("/exams/shared/invalid-token-xxxxxxxxxxxx")
    assert bad.status_code == 404
    assert b"invalid" in bad.data.lower() or b"removed" in bad.data.lower()

    rv = client.delete("/api/exams/1/share-token")
    assert rv.status_code == 204

    after = client.get(f"/exams/shared/{token}")
    assert after.status_code == 404


def test_share_token_forbidden_for_non_owner(client):
    _login(client, "bob@lab.local")
    rv = client.post("/api/exams/1/share-token")
    assert rv.status_code == 404
