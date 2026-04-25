from __future__ import annotations

import os
from datetime import date, datetime, time, timedelta
from pathlib import Path

from flask import Flask, redirect, url_for

from app.config import Config
from app.extensions import csrf, db, login_manager


def _seed_demo_data() -> None:
    from app.models import CalendarEvent, GroupMember, StudyGroup, User

    if User.query.filter_by(email="alice@lab.local").first() is not None:
        return

    alice = User(email="alice@lab.local", full_name="Alice Lab")
    alice.set_password("labdemo123")
    bob = User(email="bob@lab.local", full_name="Bob Lab")
    bob.set_password("labdemo123")
    db.session.add_all([alice, bob])
    db.session.flush()

    g = StudyGroup(name="Demo Lab Group", join_code="LABDEMO1", created_by_user_id=alice.id)
    db.session.add(g)
    db.session.flush()
    db.session.add_all(
        [
            GroupMember(group_id=g.id, user_id=alice.id, role="owner"),
            GroupMember(group_id=g.id, user_id=bob.id, role="member"),
        ]
    )

    monday = date.today() - timedelta(days=date.today().weekday())
    # Bob busy Mon 10:00–12:00; Alice busy Mon 14:00–16:00 → common free includes Mon 12:00–14:00 etc.
    db.session.add(
        CalendarEvent(
            user_id=bob.id,
            title="Lecture (seed)",
            event_type="class",
            start_at=datetime.combine(monday, time(10, 0)),
            end_at=datetime.combine(monday, time(12, 0)),
        )
    )
    db.session.add(
        CalendarEvent(
            user_id=alice.id,
            title="Tutorial (seed)",
            event_type="class",
            start_at=datetime.combine(monday, time(14, 0)),
            end_at=datetime.combine(monday, time(16, 0)),
        )
    )
    db.session.commit()


def create_app(config_object: type = Config) -> Flask:
    root = Path(__file__).resolve().parent.parent
    os.makedirs(root / "instance", exist_ok=True)

    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
    )
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login_page"

    from flask import jsonify, request

    @login_manager.unauthorized_handler
    def _unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"error": "Unauthorized"}), 401
        from flask import redirect, url_for

        return redirect(url_for("auth.login_page", next=request.url))

    from app import models  # noqa: F401

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.group_book import bp as group_book_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(group_book_bp)

    @app.get("/")
    def index():
        return redirect(url_for("group_book.group_page", group_id=1))

    with app.app_context():
        db.create_all()
        _seed_demo_data()

    return app
