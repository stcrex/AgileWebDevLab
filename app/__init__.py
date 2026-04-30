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

    g = StudyGroup(
        name="Demo Lab Group",
        join_code="LABDEMO1",
        created_by_user_id=alice.id,
    )
    db.session.add(g)
    db.session.flush()

    db.session.add_all(
        [
            GroupMember(group_id=g.id, user_id=alice.id, role="owner"),
            GroupMember(group_id=g.id, user_id=bob.id, role="member"),
        ]
    )

    monday = date.today() - timedelta(days=date.today().weekday())

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


def _seed_exam_demo_if_empty() -> None:
    from app.models import ExamResource, ExamSession, User

    alice = User.query.filter_by(email="alice@lab.local").first()
    if alice is None:
        return

    if ExamSession.query.filter_by(user_id=alice.id).first() is not None:
        return

    monday = date.today() - timedelta(days=date.today().weekday())
    start = datetime.combine(monday + timedelta(days=10), time(9, 0))
    end = start + timedelta(hours=2)

    ex = ExamSession(
        user_id=alice.id,
        title="Practice exam (seed)",
        course_code="LAB",
        starts_at=start,
        ends_at=end,
        notes="Add preparation resources on the exam detail page.",
    )

    db.session.add(ex)
    db.session.flush()

    db.session.add(
        ExamResource(
            exam_id=ex.id,
            title="Example reading (replace me)",
            url="https://www.w3.org/",
            sort_order=0,
        )
    )

    db.session.commit()


def _seed_default_courses_if_missing() -> None:
    """Lightweight catalog rows so /courses is not empty on demo accounts."""
    from app.models import Course, User

    alice = User.query.filter_by(email="alice@lab.local").first()
    if alice is None or Course.query.filter_by(owner_id=alice.id).first() is not None:
        return
    db.session.add_all(
        [
            Course(
                code="CITS3403",
                title="Agile Web Development",
                description="Flask, HTML, JSON APIs, and testing patterns used in this lab.",
                owner_id=alice.id,
            ),
            Course(
                code="LAB",
                title="Practical lab block",
                description="Aligns with course codes on seeded exam sessions (e.g. LAB).",
                owner_id=alice.id,
            ),
        ]
    )
    db.session.commit()


def _seed_demo_reminders_if_empty() -> None:
    """Optional starter reminders for the demo Alice account."""
    from datetime import datetime, timedelta

    from app.models import Reminder, User

    alice = User.query.filter_by(email="alice@lab.local").first()
    if alice is None or Reminder.query.filter_by(owner_id=alice.id).first() is not None:
        return
    due = datetime.utcnow() + timedelta(days=4)
    db.session.add_all(
        [
            Reminder(
                title="Review exam resources before your next session",
                due_at=due,
                is_done=False,
                owner_id=alice.id,
            ),
            Reminder(
                title="Coordinate a group study slot with teammates",
                due_at=None,
                is_done=False,
                owner_id=alice.id,
            ),
        ]
    )
    db.session.commit()


def _migrate_exam_share_token_column() -> None:
    """SQLite: add share_token if DB was created before this column existed."""
    from sqlalchemy import inspect, text

    try:
        insp = inspect(db.engine)
        cols = [c["name"] for c in insp.get_columns("exam_sessions")]
    except Exception:
        return

    if "share_token" in cols:
        return

    try:
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE exam_sessions ADD COLUMN share_token VARCHAR(64)"))
    except Exception:
        return

    try:
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_exam_sessions_share_token "
                    "ON exam_sessions (share_token)"
                )
            )
    except Exception:
        pass


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

        return redirect(url_for("auth.login_page", next=request.url))

    from app import models  # noqa: F401

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.exams import bp as exams_bp
    from app.blueprints.group_book import bp as group_book_bp
    from app.blueprints.reminders import bp as reminders_bp
    from app.blueprints.sidebar_stubs import bp as sidebar_stubs_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(group_book_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(sidebar_stubs_bp)
    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db_command():
        from app.seed import seed_demo_data

        db.drop_all()
        db.create_all()
        seed_demo_data()
        print("Database initialised successfully.")

    @app.get("/")
    def index():
        return redirect(url_for("exams.exams_list"))

    with app.app_context():
        db.create_all()
        _migrate_exam_share_token_column()
        _seed_demo_data()
        _seed_exam_demo_if_empty()
        _seed_default_courses_if_missing()
        _seed_demo_reminders_if_empty()

    return app
