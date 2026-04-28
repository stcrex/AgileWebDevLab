from __future__ import annotations

import secrets
from urllib.parse import urlparse

from flask import Blueprint, jsonify, render_template, request, url_for
from sqlalchemy import func
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ExamResource, ExamSession

bp = Blueprint("exams", __name__)

MAX_TITLE = 200
MAX_URL = 2048
TOKEN_NBYTES = 32


def _exam_owned(exam_id: int) -> ExamSession | None:
    ex = db.session.get(ExamSession, exam_id)
    if ex is None or ex.user_id != current_user.id:
        return None
    return ex


def _share_url_for_token(token: str) -> str:
    root = (request.url_root or "/").rstrip("/")
    return root + url_for("exams.exam_shared_public", token=token)


def _exam_by_share_token(token: str | None) -> ExamSession | None:
    if not token or len(token) > 72:
        return None
    return ExamSession.query.filter_by(share_token=token.strip()).first()


def _valid_public_url(url: str) -> bool:
    p = urlparse(url.strip())
    return p.scheme in ("http", "https") and bool(p.netloc)


@bp.get("/exams/shared/<string:token>")
def exam_shared_public(token: str):
    """Read-only exam summary for holders of an active share token (no login)."""
    ex = _exam_by_share_token(token)
    if ex is None:
        return (
            render_template(
                "exam_shared_public.html",
                ok=False,
                exam=None,
                resources=[],
            ),
            404,
        )
    rows = ex.resources.order_by(ExamResource.sort_order.asc(), ExamResource.id.asc()).all()
    return render_template(
        "exam_shared_public.html",
        ok=True,
        exam=ex,
        resources=[{"title": r.title, "url": r.url} for r in rows],
    )


@bp.get("/exams")
@login_required
def exams_list():
    rows = (
        ExamSession.query.filter_by(user_id=current_user.id)
        .order_by(ExamSession.starts_at.asc())
        .all()
    )
    return render_template("exams_list.html", exams=rows)


@bp.get("/exams/<int:exam_id>")
@login_required
def exam_detail(exam_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return render_template("exam_detail.html", exam=None, exam_id=exam_id), 404
    resources = ex.resources.order_by(ExamResource.sort_order.asc(), ExamResource.id.asc()).all()
    share_url = None
    if ex.share_token:
        share_url = _share_url_for_token(ex.share_token)
    return render_template(
        "exam_detail.html",
        exam=ex,
        exam_id=exam_id,
        resources=resources,
        share_url=share_url,
    )


@bp.post("/api/exams/<int:exam_id>/share-token")
@login_required
def api_create_or_rotate_share_token(exam_id: int):
    """Create or replace the share token with a new cryptographically random value."""
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    ex.share_token = secrets.token_urlsafe(TOKEN_NBYTES)
    db.session.commit()
    return jsonify(
        {
            "share_token": ex.share_token,
            "share_url": _share_url_for_token(ex.share_token),
        }
    ), 201


@bp.delete("/api/exams/<int:exam_id>/share-token")
@login_required
def api_revoke_share_token(exam_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    ex.share_token = None
    db.session.commit()
    return "", 204


@bp.get("/api/exams/<int:exam_id>/resources")
@login_required
def api_list_resources(exam_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    rows = ex.resources.order_by(ExamResource.sort_order.asc(), ExamResource.id.asc()).all()
    return jsonify({"resources": [r.to_dict() for r in rows]})


@bp.post("/api/exams/<int:exam_id>/resources")
@login_required
def api_create_resource(exam_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    url = (data.get("url") or "").strip()
    if not title:
        return jsonify({"error": "title is required."}), 400
    if len(title) > MAX_TITLE:
        return jsonify({"error": "title is too long."}), 400
    if not url:
        return jsonify({"error": "url is required."}), 400
    if len(url) > MAX_URL:
        return jsonify({"error": "url is too long."}), 400
    if not _valid_public_url(url):
        return jsonify({"error": "url must be an http or https URL with a host."}), 400

    mx = db.session.query(func.max(ExamResource.sort_order)).filter_by(exam_id=exam_id).scalar()
    next_order = (mx if mx is not None else -1) + 1

    r = ExamResource(exam_id=exam_id, title=title, url=url, sort_order=next_order)
    db.session.add(r)
    db.session.commit()
    return jsonify({"resource": r.to_dict()}), 201


@bp.patch("/api/exams/<int:exam_id>/resources/<int:resource_id>")
@login_required
def api_patch_resource(exam_id: int, resource_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    r = db.session.get(ExamResource, resource_id)
    if r is None or r.exam_id != exam_id:
        return jsonify({"error": "Not found."}), 404
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400
    data = request.get_json(silent=True) or {}
    if "title" in data:
        t = (data.get("title") or "").strip()
        if not t:
            return jsonify({"error": "title cannot be empty."}), 400
        if len(t) > MAX_TITLE:
            return jsonify({"error": "title is too long."}), 400
        r.title = t
    if "url" in data:
        u = (data.get("url") or "").strip()
        if not u:
            return jsonify({"error": "url cannot be empty."}), 400
        if len(u) > MAX_URL:
            return jsonify({"error": "url is too long."}), 400
        if not _valid_public_url(u):
            return jsonify({"error": "url must be an http or https URL with a host."}), 400
        r.url = u
    if "sort_order" in data:
        try:
            r.sort_order = int(data["sort_order"])
        except (TypeError, ValueError):
            return jsonify({"error": "sort_order must be an integer."}), 400
    db.session.commit()
    return jsonify({"resource": r.to_dict()})


@bp.delete("/api/exams/<int:exam_id>/resources/<int:resource_id>")
@login_required
def api_delete_resource(exam_id: int, resource_id: int):
    ex = _exam_owned(exam_id)
    if ex is None:
        return jsonify({"error": "Not found."}), 404
    r = db.session.get(ExamResource, resource_id)
    if r is None or r.exam_id != exam_id:
        return jsonify({"error": "Not found."}), 404
    db.session.delete(r)
    db.session.commit()
    return "", 204
